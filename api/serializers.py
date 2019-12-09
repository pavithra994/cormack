#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.auth.models import User
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import serializers, fields
from drf_writable_nested import WritableNestedModelSerializer
from ocom.serializers import UserSerializer as BaseUserSerializer, ActiveDateSerializerMixin, \
    timezone_formatted_datetime
from ocom.utils.permission import calculatePermissionMap
from ocom.viewsets import OcomUserRoleMixin
from ocom_xero.serializer import XeroEntitySerializer
from post_office import mail
from . import models
from api.apps import LOGGER

import datetime
import ocom.shared.api_utils as core_service

global_preferences = global_preferences_registry.manager()
User = apps.get_model('auth', 'User')
Message = apps.get_model('django_mailbox', 'Message')
MessageAttachment = apps.get_model('django_mailbox', 'MessageAttachment')

DATES_TUPLE = ('modified_date', 'created_date', 'active_start_date', 'active_end_date', )
CODE_TABLE_TUPLE = ('pk', 'id', 'code', 'description', )
SESSION_USER_ID = 'user_id'


def rejection_subject(address, task="Job"):
    return "{} Rejected: {}".format(task, address)


def send_rejection_message(recipient, sender, address, suburb, task_type, subbie, task="Job"):
    subject = "{} Rejected: {}".format(task, address)
    message = "The {} at {}, {} was Rejected for {} by {}".format(task, address, suburb, task_type, subbie)
    # send notification email
    try:
        send_mail(subject,
                  message,
                  sender,
                  recipient)
    except Exception as e:
        return HttpResponseBadRequest(e)

    return HttpResponse("OK")


def check_notes_and_notify(request, job, notes_files, recipient, is_file=False):
    """
    Traverse through notes and notify recipient

    :param request: the HTTPContext Request
    :param job: the Job model instance
    :param notes_files: the notes / files list
    :param recipient: the recipient email
    :param sender: the sender email
    :param is_file: if True, list contains files, notes otherwise
    """

    sender = global_preferences['JobEmailNotification__default_sender']

    subject = "Notification from Cormack Concreting re: Job {}".format(job.id)
    message = "There is a {} on Job {}. Click {}/ to view".format(
        "file upload" if is_file else "notification", job.id, "http://cormack.ocom.com.au/notification")

    for note in notes_files:
        if note.get('notify', False):
            # get the current instance
            if is_file:
                instance = models.FileUpload.objects.get(pk=note['id'])
            else:
                instance = models.Note.objects.get(pk=note['pk'])

            new_notification = models.JobNotification.objects.create(
                to_email=recipient,
                subject=subject,
                body=message,
                when=timezone.now()
            )

            protocol = "https://" if request.is_secure() else "http://"
            request = getattr(request, "_request", request)
            url = protocol + request.META['HTTP_HOST'] + "/notification/" + str(new_notification.guid).replace("-", "")
            message = "There is a {} on the job {}. Click {} to view".format(
                "file upload" if is_file else "notification", job.id, url)
            html_message = '<p>There is a {} on the job {}. Click {} to view</p>'.format(
                'file upload' if is_file else 'notification', job.id,
                '<a href="' + url + '">' + url + "</a>")
            new_notification.message = message
            new_notification.save()
            job.notifications.add(new_notification)
            # send email
            try:
                """
                send_mail(subject,
                          message,
                          sender,
                          [recipient], html_message=html_message)
                """

                debug_recipient = global_preferences['JobEmailNotification__debug_recipient']
                if debug_recipient and not debug_recipient == "NONE":
                    recipient = debug_recipient

                mail.send([recipient], sender, subject=subject, message=message, html_message=html_message)
            except Exception as e:
                LOGGER.error(e, exc_info=1, extra={'triggered': 'Job Notify Email', })
            finally:
                instance.send_notification = timezone.now()
                instance.save()


def get_user(request):
    """Return the currently logged in user from JWT

    :param request: the Context Request object
    :return the User instance
    :rtype: django.contrib.auth.models.User
    """

    if getattr(settings, 'JWT_LOGIN_REQUEST_CONTEXT_USER', False):
        return request.user
    else:
        user_id = request.session.get(SESSION_USER_ID, None)
        return models.User.objects.none() if user_id is None else models.User.objects.get(pk=user_id)


def filter_related_list_active_date(items):
    """Return items that are still active on a related list

    :param items: the list of items to filter
    :returns the filtered items
    :rtype: list
    """

    filtered = []

    for item in items:
        if 'active_start_date' not in item and item['active_end_date'] is not None:
            pass
        else:
            filtered.append(item)

    return filtered


def save_note_source(request=None, queryset=None, user=None):
    """Update Note to point user account as owner

    :param rest_framework.request.Request request: the drf request object to refer to
    :param queryset: the queryset to iterate values from
    :param user: auth user instance
    """

    author = user if user else OcomUserRoleMixin.get_user(request)

    if author:
        for note in queryset:
            if note.who is None:
                note.who = str(author)
                note.save()


def get_file_guid(file):
    """Return the guid of the file

    :param api.models.FileUpload file: the fileUpload model instance
    :return: the guid
    :rtype: str
    """

    try:
        return str(file.url_guid).replace('-', '')
    except models.FileUpload.DoesNotExist:
        return ''


def update_file_types(files, data_with_file_type, file_key='files'):
    """Update file types of files based on data input

    :param list files: the list of files to search for
    :param dict data_with_file_type: the data with updated file types info
    :param str file_key: the file key to use with data_with_file_type
    """

    initial_files = data_with_file_type.get(file_key, [])
    file_ids = [file['id'] for file in files]

    for initial_file in initial_files:
        if initial_file['id'] in file_ids and 'file_type' in initial_file:
            file = models.FileUpload.objects.get(pk=initial_file['id'])
            new_value = initial_file['file_type']

            if new_value is not None:
                new_value = models.CodeFileType.objects.get(pk=new_value)

            if file.file_type != new_value:
                file.file_type = new_value
                file.save()


# This is used as a test serializer for displaying validation errors. not intended for production!
# Example usage: class YourSerializer(TestValidationSerializer, someSerializerClass): ...
class TestValidationSerializer(serializers.ModelSerializer):
    # Note: this is a test validation to force all fields as invalid (useful for checking server error message display)
    def validate(self, attrs):
        test_errors = dict()
        for index, item in enumerate(JobSerializer.Meta.fields):
            if item not in ['pk', 'id']:
                test_errors[item] = 'Test validation error for {}: {}!'.format(index, item)

        raise serializers.ValidationError(test_errors)


class CodeJobTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeJobType
        fields = CODE_TABLE_TUPLE + ('background_colour', 'foreground_colour', ) + DATES_TUPLE
        depth = 1


class CodeFileTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeFileType
        fields = CODE_TABLE_TUPLE + ('can_email', 'is_internal',) + DATES_TUPLE
        depth = 1


class CodeMixSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeMix
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodeSubbieTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeSubbieType
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodePavingColourSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodePavingColour
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodePavingTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodePavingType
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodePurchaseOrderTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodePurchaseOrderType
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodeDrainTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeDrainType
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1

class CodeDepotTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeDepotType
        fields = CODE_TABLE_TUPLE + ('background_colour', 'foreground_colour', ) + DATES_TUPLE
        depth = 1

class CodeRepairTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeRepairType
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class CodeTaskTypeSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeTaskType
        fields = CODE_TABLE_TUPLE + ('background_colour', 'foreground_colour', 'job_date_field', 'subbie_field',
                                     'job_date_order') + DATES_TUPLE
        depth = 1


class CodeTimeOfDaySerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.CodeTimeOfDay
        fields = CODE_TABLE_TUPLE + DATES_TUPLE
        depth = 1


class NoteSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    # when_formatted = fields.DateTimeField(format=settings.DATETIME_FORMAT, source='when', read_only=True)
    when_formatted = serializers.SerializerMethodField()
    # who = UserSerializer(required=False, read_only=True)
    editable = serializers.SerializerMethodField()
    owned = serializers.SerializerMethodField()
    hidden_actual = serializers.SerializerMethodField()
    # notify = serializers.BooleanField(default=False)

    class Meta:
        model = models.Note
        fields = '__all__'

    # noinspection PyMethodMayBeStatic
    def is_owned(self, obj):
        user = OcomUserRoleMixin.get_user(self.context['request'])

        # allow administrators to remove any notes
        if user.role.administrator:
            return True

        if obj.who is not None:
            return str(user) == obj.who
        else:
            return False

    def get_editable(self, obj):
        """Return true when note date is posted within 24 hours and belongs to the current user"""

        return obj.when >= timezone.now() - datetime.timedelta(days=1) if self.is_owned(obj) else False

    def get_owned(self, obj):
        """Return true when note is owned by user"""

        return self.is_owned(obj)

    # noinspection PyMethodMayBeStatic
    def get_hidden_actual(self, obj):
        """Return true if note should be hidden from view by another account.
        Notes owned by an account whether hidden or not is always visible to the owner"""

        return False if self.is_owned(obj) else obj.hide

    # noinspection PyMethodMayBeStatic
    def get_when_formatted(self, obj):
        """Return timezone-aware formatted 'when' Date"""

        return timezone_formatted_datetime(obj.when)


class JobCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobCost
        fields = '__all__'
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class JobDrainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobDrains
        fields = '__all__'
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class JobPurchaseOrderSerializer(WritableNestedModelSerializer):
    class Meta:
        model = models.JobPurchaseOrder
        fields = '__all__'


class JobNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobNotification
        fields = '__all__'
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class TaskSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    address = serializers.SerializerMethodField()
    job_description = serializers.SerializerMethodField()
    suburb = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    task_type_label = serializers.SerializerMethodField()
    supplier_label = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = '__all__'

    def update(self, instance, validated_data):
        # check if accepted date is set or not
        if not instance.accepted_date and validated_data.get('accepted_date'):
            # send notification email?
            pass

        # check if rejected_date is set or not
        if not instance.rejected_date and validated_data.get('rejected_date'):
            task_type_label = instance.task_type.description if instance.task_type else ""
            supplier_label = instance.supplier.name if instance.supplier else ""

            send_rejection_message(
                [global_preferences['RejectedEmailNotification__job_reject_email']],
                global_preferences['RejectedEmailNotification__email_sender'],
                instance.job.address,
                instance.job.suburb,
                task_type_label,
                supplier_label)
            # look for replacement subbie
            subbie = models.Subbie.objects.get(id=global_preferences['RejectedEmailNotification__default_subbie_id'])

            if subbie:
                validated_data['supplier'] = subbie

        return super(TaskSerializer, self).update(instance, validated_data)

    def validate(self, data):
        base_query = models.Task.objects.filter(job=data['job'])
        # check if new so no self.id check
        # if 'id' in self.initial_data:
        #     query_duplicates = base_query.filter(task_type=data['task_type']).exclude(id=self.initial_data['id'])
        # else:
        #     query_duplicates = base_query.filter(task_type=data['task_type'])
        #
        # if len(query_duplicates) > 0:
        #     raise serializers.ValidationError("Job with the same Task Type already exists!")

        if data['task_type'].job_date_order > 0 and data['date_scheduled']:
            date_query = base_query.filter(Q(task_type__job_date_order__gt=data['task_type'].job_date_order,
                                           date_scheduled__lt=data['date_scheduled']) |
                                           Q(task_type__job_date_order__lt=data['task_type'].job_date_order,
                                           date_scheduled__gt=data['date_scheduled']))

            task = date_query.first()
            if task: # If we have one show an error.
                raise serializers.ValidationError(
                    "{} Scheduled date should be greater than {} Schedule date ({}).".format(
                        data['task_type'].description,
                        task.task_type.description,
                        task.date_scheduled.strftime(settings.DATETIME_FORMAT)))

        # TODO: group into jobs and repairs so a repair with a job with the same task types are ok
        return data

    # noinspection PyMethodMayBeStatic
    def get_task_type_label(self, instance):
        if instance.task_type:
            return instance.task_type.description

        return ""

    # noinspection PyMethodMayBeStatic
    def get_supplier_label(self, instance):
        if instance.supplier:
            return instance.supplier.name

        return "Unknown"

    # noinspection PyMethodMayBeStatic
    def get_address(self, instance):
        if instance.job:
            return instance.job.address

        return "Unknown"

    # noinspection PyMethodMayBeStatic
    def get_job_description(self, instance):
        if instance.job:
            return instance.job.description

        return "Unknown"

    # noinspection PyMethodMayBeStatic
    def get_suburb(self, instance):
        if instance.job:
            return instance.job.suburb

        return "Unknown"

    # noinspection PyMethodMayBeStatic
    def get_client(self, instance):
        if instance.job:
            return instance.job.client.name

        return "Unknown"


class RepairCostSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RepairCost
        fields = '__all__'
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class FileUploadFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileUpload
        fields = ('id', 'file_type', '_is_deleted', '_display_order', 'send_notification')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class FileUploadSerializer(serializers.ModelSerializer):
    # when_uploaded = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=False)
    can_email = serializers.SerializerMethodField()
    when_uploaded = serializers.SerializerMethodField()
    # who_uploaded = UserSerializer(required=False)
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.FileUpload
        fields = '__all__'
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }

    # noinspection PyMethodMayBeStatic
    def get_when_uploaded(self, instance):
        try:
            return timezone_formatted_datetime(instance.when_uploaded)
        except AttributeError:
            return None

    # noinspection PyMethodMayBeStatic
    def get_can_email(self, instance):
        try:
            return instance.file_type.can_email
        except AttributeError:
            return False

    # noinspection PyMethodMayBeStatic
    def get_url(self, instance):
        try:
            return get_file_guid(instance)
        except AttributeError:
            return ''


class JobSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    client = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=models.Client.objects.all())
    job_type = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                  queryset=models.CodeJobType.objects.all())
    mix = serializers.PrimaryKeyRelatedField(many=False, required=False, allow_null=True,
                                             queryset=models.CodeMix.objects.all())
    estimated_cost = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    supervisor_mobile_number = serializers.SerializerMethodField()
    supervisor_email = serializers.SerializerMethodField()
    # multiple files model here, before start_date
    dollars_difference = serializers.SerializerMethodField()
    sub_contractor = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                        queryset=models.Subbie.objects.all(), allow_null=True)
    
    base_inspector = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                        queryset=models.Subbie.objects.all(), allow_null=True)

    pump_inspector = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                        queryset=models.Subbie.objects.all(), allow_null=True)
    
    supervisor = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                    queryset=models.Supervisor.objects.all(), allow_null=True)
    paving_colour = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                       queryset=models.CodePavingColour.objects.all(), allow_null=True)
    paving_type = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                     queryset=models.CodePavingType.objects.all(), allow_null=True)
    drain_type = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                    queryset=models.CodeDrainType.objects.all(), allow_null=True)
    depot_type = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                  queryset=models.CodeDepotType.objects.all())
    pour_date_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                               queryset=models.CodeTimeOfDay.objects.all(),
                                                               allow_null=True)
    base_inspection_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                     queryset=models.CodeTimeOfDay.objects.all(),
                                                                     allow_null=True)
    steel_inspection_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                      queryset=models.CodeTimeOfDay.objects.all(),
                                                                      allow_null=True)
    rock_booked_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                 queryset=models.CodeTimeOfDay.objects.all(),
                                                                 allow_null=True)
    part_a_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                            queryset=models.CodeTimeOfDay.objects.all(),
                                                            allow_null=True)
    waste_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                           queryset=models.CodeTimeOfDay.objects.all(), allow_null=True)
    piers_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                           queryset=models.CodeTimeOfDay.objects.all(), allow_null=True)
    piers_inspection_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                      queryset=models.CodeTimeOfDay.objects.all(),
                                                                      allow_null=True)
    piers_concrete_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                      queryset=models.CodeTimeOfDay.objects.all(),
                                                                      allow_null=True)
    steel_delivery_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                    queryset=models.CodeTimeOfDay.objects.all(),
                                                                    allow_null=True)
    pod_delivery_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                  queryset=models.CodeTimeOfDay.objects.all(),
                                                                  allow_null=True)
    job_costs = JobCostSerializer(many=True, required=False, allow_null=True)
    job_drains = JobDrainsSerializer(many=True, required=False, allow_null=True)
    files = FileUploadFormSerializer(many=True, required=False, allow_null=True)
    notes = NoteSerializer(many=True, required=False, allow_null=True, partial=True)
    purchase_orders = JobPurchaseOrderSerializer(many=True, required=False, allow_null=True)
    xero_purchase_order = XeroEntitySerializer(many=False, required=False, allow_null=True)

    building_inspector_supplier = serializers.PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, required=False,
                                                            queryset=models.CodeSupplier.objects.all())
    termite_supplier = serializers.PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, required=False,
                                                          queryset=models.CodeSupplier.objects.all())

    notifications = JobNotificationSerializer(many=True, required=False, allow_null=True)

    rock_supplier = serializers.PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, required=False,
                                                            queryset=models.CodeSupplier.objects.all())

    pod_supplier = serializers.PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, required=False,
                                                            queryset=models.CodeSupplier.objects.all())

    steel_supplier = serializers.PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, required=False,
                                                            queryset=models.CodeSupplier.objects.all())


    concrete_time_of_day = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                                      queryset=models.CodeTimeOfDay.objects.all(),
                                                                      allow_null=True)

    class Meta:
        model = models.Job
        fields = ('pk', 'id', 'is_active', 'date_received', 'job_type', 'mix', 'description',
                  'comments', 'address', 'suburb', 'client', 'purchase_order_number', 'job_number',
                  'purchase_order_value', 'sqm', 'sub_contractor', 'estimated_cost', 'pour_date','pour_date_time_of_day', 'pour_date_notes',
                  'supervisor', 'supervisor_name', 'supervisor_mobile_number', 'supervisor_email',
                  'base_inspection_date', 'base_inspection_date_notes', 'steel_inspection_date', 'steel_inspection_date_notes', 'rock_m3', 'rock_booked_date', 'rock_booked_date_notes', 'materials',
                  'materials_time', 'has_part_a', 'part_a_date', 'part_a_date_notes', 'part_a_booking_number', 'waste_date', 'piers_date','piers_date_notes',
                  'piers_inspection_date', 'piers_inspection_time_of_day', 'piers_inspection_date_notes', 'pier_concrete', 'pier_concrete_notes', 'piers_concrete_date', 'start_date', 'call_up_date', 'call_up_date_notes', 'take_off_sent',
                  'proposed_start_date', 'paving_colour', 'excavation_allowance', 'paving_type', 'date_cancelled',
                  'drains', 'drain_type', 'depot_type', 'has_conduit', 'dollars_difference', 'job_costs', 'job_drains', 'files',
                  'notes', 'purchase_orders', 'xero_purchase_order', 'type_list',
                  'dug_date', 'prepared_date', 'poured_date', 'cut_date', 'sealed_date',
                  'base_inspection_time_of_day', 'steel_inspection_time_of_day',
                  'rock_booked_time_of_day', 'part_a_time_of_day', 'waste_time_of_day', 'piers_time_of_day',
                  'piers_inspection_time_of_day','piers_concrete_time_of_day' , 'steel_delivery_date', 'steel_delivery_time_of_day', 'steel_delivery_date_notes',
                  'pod_delivery_date', 'pod_delivery_date_notes', 'pod_delivery_time_of_day', 'building_inspector_supplier',
                  'termite_supplier', 'notifications', 'rock_supplier', 'pod_supplier',
                  'steel_supplier','down_pipes_installed', 'down_pipes_comment', 'gas_line_installed',
                  'gas_line_comment', 'rebates_brickwork', 'rebates_brickwork_comment', 'risers_correct_location',
                  'risers_location_comment', 'good_access_rear_paving', 'rear_paving_comment',
                  'pacing_within_tolerance', 'pacing_heights_comment', 'contractor_swms', 'approved_date', 'code',
                  'set_out_date', 'drain_date', 'wanted_pour_date','wanted_pour_date_notes', 'piers', 'pier_inspection_done',
                  'base_inspection_done', 'steel_inspection_done', 'concrete_date', 'concrete_date_notes', 'concrete_time_of_day', 'concrete_mix', 'slab_schedule_notes',
                  'base_inspector', 'pump_inspector','base_date', 'base_date_notes',) + DATES_TUPLE
        depth = 1

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_estimated_cost(self, instance):
        try:
            return instance.sub_contractor.rate_per_m * instance.sqm
        except (AttributeError, TypeError):
            return 0

    # noinspection PyMethodMayBeStatic
    def get_supervisor_name(self, instance):
        try:
            return instance.supervisor.name
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_supervisor_mobile_number(self, instance):
        try:
            return instance.supervisor.phone_number
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_supervisor_email(self, instance):
        try:
            return instance.supervisor.email
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_dollars_difference(self, instance):
        total = 0

        try:
            for job_cost in instance.job_costs:
                total += instance.job_costs.quantity * instance.job_costs.unit_price
        except TypeError:
            pass

        return total

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        job_costs = validated_data.pop('job_costs', [])
        job_drains = validated_data.pop('job_drains', [])
        purchase_orders = validated_data.pop('purchase_orders', [])
        job = super(JobSerializer, self).create(validated_data)

        for file in files:
            job.files.add(models.FileUpload.objects.get(pk=file.get('id')))

        # filter out job_costs
        job_costs_save = filter_related_list_active_date(job_costs)
        job_drains_save = filter_related_list_active_date(job_drains)
        # save related models
        core_service.update_model_relation('JobCost', 'job_costs', job, job_costs_save, True)
        core_service.update_model_relation('JobDrains', 'job_drains', job, job_drains_save, True)
        core_service.update_model_relation('JobPurchaseOrder', 'purchase_orders', job, purchase_orders, True)

        if 'request' in self.context:
            # check notes for notify
            notes = self.initial_data.get('notes', [])
            base_files = self.initial_data.get('files', [])
            user = OcomUserRoleMixin.get_user(self.context['request'])

            recipient = global_preferences['JobEmailNotification__default_recipient']

            # check if user is not supervisor
            if not user.role.supervisor:
                # check if supervisor is set in job
                if job.supervisor:
                    recipient = job.supervisor.email

            check_notes_and_notify(self.context['request'], job, notes, recipient)
            check_notes_and_notify(self.context['request'], job, base_files, recipient, is_file=True)

        return job

    def update(self, instance, validated_data):
        file_key = 'files'
        files = validated_data.pop(file_key, [])
        cost_key = 'job_costs'
        job_costs = validated_data.pop(cost_key, [])
        job_drains = validated_data.pop('job_drains', [])
        purchase_orders = validated_data.pop('purchase_orders', [])

        update_file_types(files, self.initial_data, file_key)
        new_comment = validated_data.get('comments')
        old_comment = getattr(instance, 'comments')
        instance = super(JobSerializer, self).update(instance, validated_data)
        if not self.partial:
            # filter out job_costs
            job_costs_save = filter_related_list_active_date(job_costs)
            job_drains_save = filter_related_list_active_date(job_drains)
            # save related models
            core_service.update_model_relation('FileUpload', file_key, instance, files, True)
            core_service.update_model_relation('JobCost', cost_key, instance, job_costs_save, True)
            core_service.update_model_relation('JobDrains', 'job_drains', instance, job_drains_save, True)
            core_service.update_model_relation('JobPurchaseOrder', 'purchase_orders', instance, purchase_orders, True)

            if 'request' in self.context:
                # check notes for notify
                notes = self.initial_data.get('notes', [])
                base_files = self.initial_data.get('files', [])
                user = OcomUserRoleMixin.get_user(self.context['request'])
                recipient = global_preferences['JobEmailNotification__default_recipient']

                # check if user is not supervisor
                if not user.role.supervisor:
                    # check if supervisor is set in job
                    if instance.supervisor:
                        recipient = instance.supervisor.email

                check_notes_and_notify(self.context['request'], instance, notes, recipient)
                check_notes_and_notify(self.context['request'], instance, base_files, recipient,
                                       is_file=True)

        # we swallow the errors and log them to sentry for now
        try:
            # check initial data for file_type changes
            if new_comment is not None:
                old_comment = old_comment.strip() if isinstance(old_comment, str) else ''
                new_comment = new_comment.strip() if isinstance(new_comment, str) else ''

                if new_comment != old_comment and old_comment != '' and not instance.notes.filter(
                        job=instance, note=old_comment).exists():
                        # add old comment to notes
                        instance.notes.create(note=old_comment)

            if 'request' in self.context:
                save_note_source(self.context['request'], models.Note.objects.filter(job=instance))

        except Exception as e:
            LOGGER.error(e, exc_info=1, extra={'triggered': 'Job Update', })

        return instance


class RepairSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    repair_type_label = serializers.SerializerMethodField()
    repair_subbie_label = serializers.SerializerMethodField()
    address_label = serializers.SerializerMethodField()
    suburb_label = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    job = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=models.Job.objects.all(),
                                             allow_null=True, required=False)
    repair_subbie = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                       queryset=models.Subbie.objects.all())
    repair_type = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                     queryset=models.CodeRepairType.objects.all())
    repair_costs = RepairCostSerializer(many=True, required=False, allow_null=True)
    files = FileUploadFormSerializer(many=True, required=False, allow_null=True)
    notes = NoteSerializer(many=True, required=False, allow_null=True)
    xero_purchase_order = XeroEntitySerializer(many=False, required=False, allow_null=True)

    supervisor_name = serializers.SerializerMethodField()
    supervisor_mobile_number = serializers.SerializerMethodField()
    supervisor_email = serializers.SerializerMethodField()
    supervisor = serializers.PrimaryKeyRelatedField(many=False, read_only=False, required=False,
                                                    queryset=models.Supervisor.objects.all(), allow_null=True)

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        repair_costs = validated_data.pop('repair_costs', [])
        repair = super(RepairSerializer, self).create(validated_data)

        for file in files:
            repair.files.add(models.FileUpload.objects.get(pk=file.get('id')))

        # filter out repair_costs
        repair_costs_save = filter_related_list_active_date(repair_costs)
        # save related models
        core_service.update_model_relation('RepairCost', 'repair_costs', repair, repair_costs_save, True)

        if 'request' in self.context:
            save_note_source(self.context['request'], models.Note.objects.filter(repair=repair))

        return repair

    def update(self, instance, validated_data):
        # check if accepted date is set or not
        if not instance.accepted_date and validated_data.get('accepted_date'):
            # send notification email?
            pass

        # check if rejected_date is set or not
        if not instance.rejected_date and validated_data.get('rejected_date'):
            send_rejection_message(
                [global_preferences['RejectedEmailNotification__repair_reject_email']],
                global_preferences['RejectedEmailNotification__email_sender'],
                instance.job.address,
                instance.job.suburb,
                instance.repair_type.description,
                instance.repair_subbie.name,
                "Repair")
            # look for replacement subbie
            subbie = models.Subbie.objects.get(id=global_preferences['RejectedEmailNotification__default_subbie_id'])

            if subbie:
                validated_data['repair_subbie'] = subbie

        file_key = 'files'
        files = validated_data.pop(file_key, [])
        cost_key = 'repair_costs'
        repair_costs = validated_data.pop(cost_key, [])
        update_file_types(files, self.initial_data, file_key)
        new_comment = validated_data.get('comments')
        old_comment = getattr(instance, 'comments')
        instance = super(RepairSerializer, self).update(instance, validated_data)
        # filter out repair_costs
        repair_costs_save = filter_related_list_active_date(repair_costs)
        # save related models
        core_service.update_model_relation('FileUpload', file_key, instance, files, True)
        core_service.update_model_relation('RepairCost', cost_key, instance, repair_costs_save, True)

        # we swallow the errors and log them to sentry for now
        try:
            # check initial data for file_type changes
            if new_comment is not None:
                old_comment = old_comment.strip() if isinstance(old_comment, str) else ''
                new_comment = new_comment.strip() if isinstance(new_comment, str) else ''

                if new_comment != old_comment and old_comment != '' and not instance.notes.filter(
                        repair=instance, note=old_comment).exists():
                        # add old comment to notes
                        instance.notes.create(note=old_comment)

            if 'request' in self.context:
                save_note_source(self.context['request'], models.Note.objects.filter(repair=instance))

        except Exception as e:
            LOGGER.error(e, exc_info=1, extra={'triggered': 'Repair Update', })

        return instance

    # noinspection PyMethodMayBeStatic
    def get_repair_subbie_label(self, instance):
        try:
            return instance.repair_subbie.name
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_repair_type_label(self, instance):
        try:
            return instance.repair_type.description
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_address_label(self, instance):
        try:
            return instance.job.address
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_suburb_label(self, instance):
        try:
            return instance.job.suburb
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_client_name(self, instance):
        try:
            return instance.job.client.name
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_supervisor_name(self, instance):
        try:
            return instance.supervisor.name
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_supervisor_mobile_number(self, instance):
        try:
            return instance.supervisor.phone_number
        except AttributeError:
            return ''

    # noinspection PyMethodMayBeStatic
    def get_supervisor_email(self, instance):
        try:
            return instance.supervisor.email
        except AttributeError:
            return ''

    class Meta:
        model = models.Repair
        fields = ('pk', 'id', 'is_active', 'date_received', 'end_date', 'end_date_notes', 'job', 'repair_subbie', 'repair_type', 'repair_type_label',
                  'repair_subbie_label', 'address_label', 'suburb_label', 'client_name', 'description', 'comments',
                  'po_number', 'accepted_date', 'rejected_date', 'back_charge', 'permit_number', 'due_date', 'start_by',
                  'amount', 'completed_date', 'repair_costs', 'files', 'notes', 'xero_purchase_order',
                  'supervisor_name', 'supervisor_mobile_number', 'supervisor_email', 'supervisor',
                  'address', 'suburb', 'no_job','repair_amount') + DATES_TUPLE
        depth = 1


class SubbieSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.Subbie
        fields = '__all__'
        depth = 1

class SupervisorSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.Supervisor
        fields = '__all__'
        depth = 1


class ClientManagerSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.ClientManager
        fields = '__all__'
        depth = 1


class ClientSerializer(ActiveDateSerializerMixin, WritableNestedModelSerializer):
    class Meta:
        model = models.Client
        fields = '__all__'
        depth = 1


class RoleSerializer(serializers.ModelSerializer):
    subbie_id = serializers.SerializerMethodField()
    supervisor_id = serializers.SerializerMethodField()
    can_see_plans_before_accept = serializers.SerializerMethodField()

    class Meta:
        model = models.Role
        fields = ('id', 'administrator', 'supervisor', 'subcontractor', 'client_manager',
                  'can_see_plans_before_accept', 'employee',
                  'subbie_id', 'supervisor_id') + DATES_TUPLE

    # noinspection PyMethodMayBeStatic
    def get_can_see_plans_before_accept(self, instance: models.Role):
        if instance.administrator or instance.supervisor:
            return True

        if instance.subcontractor:
            subbie = models.Subbie.objects.get(user=instance.user)
            return subbie.can_see_plans_before_accept if subbie else False
        else:
            # assume False for everyone else
            return False

    # noinspection PyMethodMayBeStatic
    def get_subbie_id(self, instance: models.Role):
        if instance.subcontractor:
            subbie = models.Subbie.objects.get(user=instance.user)
            if subbie:
                return subbie.id

        return None

    # noinspection PyMethodMayBeStatic
    def get_supervisor_id(self, instance: models.Role):
        if instance.supervisor:
            superman = models.Supervisor.objects.get(user=instance.user)
            if superman:
                return superman.id

        return None


class UserSerializer(BaseUserSerializer):
    role = RoleSerializer()
    _permissionMap = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions',
                  'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'descriptive_name', 'role',
                  '_permissionMap',)
        depth = 1       # apparently adds Role to relationships in User model

    # noinspection PyMethodMayBeStatic
    def get__permissionMap(self, obj):
        return calculatePermissionMap(obj)

class HashSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hash
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = '__all__'


class MailMessagesSerializer(OcomUserRoleMixin, serializers.ModelSerializer):
    fetched = fields.DateTimeField(format=settings.DATETIME_FORMAT, source='processed', read_only=True)
    from_email = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, required=False, allow_null=True, read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'mailbox', 'attachments', 'subject', 'from_email', 'to_addresses', 'text', 'fetched', )

    # noinspection PyMethodMayBeStatic
    def get_from_email(self, obj):
        return obj.from_address[0]

    def update(self, instance, validated_data):
        attachments = self.initial_data.get('attachments', [])
        instance = super(MailMessagesSerializer, self).update(instance, validated_data)
        active_jobs = self.initial_data.get('active_jobs')
        save_to = self.initial_data.get('save_to', '')
        repairs = self.initial_data.get('repairs')

        who = self.get_user(self.context['request'])
        files = []
        note = self.initial_data.get('text', '')

        for attachment in attachments:
            if attachment['include']:
                files.append(attachment)

        """
        if active_jobs and save_to == 'jobs':
            for active_job in active_jobs:
                # replicate each file into a new attachment for EACH job
                job = Job.objects.get(pk=active_job['id'])
                upload_files_for_related_model(files=files, related_model=job, who=who)

                if note != '':
                    job.notes.create(note=note, who=who)

        if repairs and save_to == 'repairs':
            for repair in repairs:
                # replicate each file into a new attachment for EACH repair
                selected_repair = Repair.objects.get(pk=repair['id'])
                upload_files_for_related_model(files=files, related_model=selected_repair, who=who,
                                               file_model_name='repair_files')

                if note != '':
                    selected_repair.repair_notes.create(note=note, who=who)
        """

        return instance
