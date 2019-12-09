#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Q
from django_mailbox.models import MessageAttachment
from rest_framework import response, status, viewsets
from rest_framework.filters import BaseFilterBackend
from urllib.parse import urlparse
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from ocom.shared.filters import FilterFilter
from ocom.shared.queryset_utils import filter_queryset_by_active_status
from ocom.utils.drf_views_snippets import filter_queryset
from ocom.viewsets import OcomModelViewSet, OcomUserRoleMixin
from query.filter.query_filter import QueryFilter
from . import models, serializers
from django.contrib.auth.models import User

import datetime
import django_filters
import boto
import copy
import os
import ocom.shared.api_utils as core_service


Message = apps.get_model('django_mailbox', 'Message')


def get_queryset_with_role(query_params, queryset, user, fields):
    """Returns queryset based on role

    :param dict query_params: the query parameters
    :param queryset: the queryset to filter
    :param user: the User model instance
    :param list fields: the list of fields to filter with
    :return: The filtered queryset
    """

    try:
        if not user or user.role is None:
            return models.Client.objects.none()
    except ObjectDoesNotExist:
        return models.Client.objects.none()

    # prevent non-administrator accounts from accessing inactive queries
    with_active_date = not user.role.administrator
    return filter_queryset(query_params, queryset, fields, with_active_date=with_active_date)


def get_email_source_files(request):
    """Returns the list of files from request.data if the 'email' flag for it is True

    :param rest_framework.request.Request request: the drf request object to refer to
    :return: The list of files
    :rtype: list
    """

    return request.data.pop('files', None) if request.data.get('email', False) else []


def upload_files_for_related_model(files=None, related_model=None, who=None, file_model_name='files'):
    """Attach files from a given source with MessageAttachment and update relationship to specified model instance

    :param list files: the files (including path) to add to the FileUpload model
    :param django.db.models.Model related_model: the model instance to relate the file upload to (currently allowed
    are Job and Repair)
    :param django.contrib.auth.models.User who: the user account who was tagged as the file uploader
    :param str file_model_name: the file model resource name (e.g. 'files' for Job, 'repair_files' for Repair)
    """

    new_files = []

    for file in files:
        attachment = MessageAttachment.objects.get(pk=file['id'])
        # may not be compatible with windows path
        file_path = settings.MEDIA_ROOT + '/' + str(attachment.document)
        file_type_id = None if file['file_type'] == '' else int(file['file_type'])
        file_type = models.CodeFileType.objects.get(pk=file_type_id) if file_type_id is not None else None
        raw_file = ContentFile(attachment.document.read())
        raw_file.name = os.path.basename(file_path)
        new_file = models.FileUpload.objects.create(file=raw_file, file_type=file_type,
                                                    name=os.path.basename(file_path), who_uploaded=who)
        new_files.append({
            'id': new_file.id,
            '_display_order': 0,
            '_is_deleted': False,
        })

    core_service.update_model_relation('FileUpload', file_model_name, related_model, new_files, True)


def get_file_url(url_path, parent_dir='/uploads/', strict=False):
    return url_path


def filter_queryset_by_range_dates(queryset, date_field, start_date=None, end_date=None):
    """Filter queryset by Date Range

    :param queryset: the queryset to filter
    :param str date_field: the name of the date field
    :param start_date: the starting date range
    :param end_date: the end date range
    :return: the filtered queryset
    """

    updated_queryset = queryset

    if date_field == "client":
        actual_date_field = "client__when"
    elif date_field == "soa":
        actual_date_field = "client__date_soa"
    elif date_field == "paid":
        actual_date_field = "date_paid"
    else:
        return updated_queryset

    if start_date:
        the_filter = {
            actual_date_field + '__gte': start_date
        }
        updated_queryset = updated_queryset.filter(**the_filter)

    if end_date:
        the_filter = {
            actual_date_field + '__lte': end_date
        }
        updated_queryset = updated_queryset.filter(**the_filter)

    return updated_queryset


class StandardFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return filter_queryset(request.query_params, queryset, with_active_date=False)


class CommonViewset(OcomUserRoleMixin, OcomModelViewSet):
    pass


class ActiveCommonViewset(CommonViewset):
    def get_queryset(self):
        # check logged-in user
        user = self.get_user(self.request)
        all_fields = self.request.GET.getlist('fieldList')
        return get_queryset_with_role(self.request.query_params, self.queryset, user, all_fields)


class JobFilterSet(django_filters.FilterSet):
    job_type = django_filters.ModelChoiceFilter(queryset=models.CodeJobType.objects.all())
    depot_type = django_filters.ModelChoiceFilter(queryset=models.CodeDepotType.objects.all())
    pour_date__ge = django_filters.IsoDateTimeFilter(name='pour_date', lookup_expr='gte')
    supervisor = django_filters.ModelChoiceFilter(queryset=models.Supervisor.objects.all())

    class Meta:
        model = models.Job
        fields = []


class JobViewSet(ActiveCommonViewset):
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer
    filter_backends = (DjangoFilterBackend, FilterFilter, StandardFilter, QueryFilter, SearchFilter, OrderingFilter)
    filter_class = JobFilterSet

    ordering_fields = ('call_up_date', 'call_up_date_notes', 'pour_date', 'pour_date_time_of_day','pour_date_notes', 'address', 'sqm', 'paving_colour__description',
                       'excavation_allowance', 'client__name', 'supervisor__name', 'comments', 'type_list',
                       'building_inspector_supplier__description', 'piers_inspection_date', 'piers_inspection_time_of_day','piers_inspection_date_notes','pier_concrete', 'pier_concrete_notes', 'piers_concrete_date'
                       'rock_supplier__description', 'termite_supplier__description', 'part_a_date', 'part_a_date_notes',
                       'pod_supplier__description', 'sub_contractor__email', 'base_inspection_date', 'base_inspection_date_notes', 
                       'steel_inspection_date', 'steel_inspection_date_notes', 'waste_date', 'set_out_date', 'drain_date', 'wanted_pour_date','wanted_pour_date_notes','piers_date',
                       'piers_date_notes','rock_booked_date' , 'rock_booked_date_notes', 'pod_delivery_date', 'pod_delivery_date_notes',
                       'pier_inspection_done', 'base_inspection_done','steel_inspection_done', 'concrete_date', 'concrete_date_notes', 'concrete_time_of_day',
                       'concrete_mix', 'slab_schedule_notes', 'base_inspector__email', 'pump_inspector__description','base_date', 'base_date_notes', 'steel_delivery_date', 'steel_delivery_date_notes',)
    search_fields = ('address', 'suburb', 'client__name', 'purchase_order_number', 'suburb', 'supervisor__name',
                     'job_number', 'description', 'code')

    def get_queryset(self):
        user = self.get_user(self.request)
        queryset = models.Job.objects.all()

        if user.is_staff or user.is_superuser:
            return queryset
        else:
            role = models.Role.objects.get(user=user)
            if role:
                if role.employee:
                    return queryset

                if role.supervisor:
                    super_man = models.Supervisor.objects.get(user=user)
                    queryset = queryset.filter(supervisor=super_man) if super_man else queryset.none()

                if role.client_manager:
                    manager = models.ClientManager.objects.get(user=user)
                    queryset = queryset.filter(client=manager.client) if manager else queryset.none()

                if role.subcontractor:
                    subbie = models.Subbie.objects.get(user=user)

                    if subbie:
                        tasks = models.Task.objects.filter(supplier=subbie).values_list('job', flat=True)
                        non_slab_jobs = models.Job.objects.filter(
                            sub_contractor=subbie, job_type_id__in=[2, 3]).values_list('id', flat=True)

                        # search repairs only when pk is in kwargs
                        if 'pk' in self.kwargs:
                            repairs = models.Repair.objects.filter(repair_subbie=subbie).values_list('job', flat=True)

                            # we also need to allow jobs related to repairs
                            if not subbie.can_see_plans_before_accept:
                                repairs = repairs.filter(rejected_date__isnull=True)

                            merged = list(set().union(tasks, non_slab_jobs, repairs))
                            queryset = queryset.filter(pk__in=merged)
                        else:
                            queryset = queryset.filter(pk__in=list(set().union(tasks, non_slab_jobs)))
                    else:
                        queryset = queryset.none()
            else:
                # it not staff/superuser then return nothing as there is no Role
                if not user.is_staff and not user.is_superuser:
                    queryset = queryset.none()
        return queryset

    def create(self, request, *args, **kwargs):
        # intercept request.data and get the files to save from here if it came from email
        files = get_email_source_files(request)
        result = super(JobViewSet, self).create(request, *args, **kwargs)

        if files:
            who = self.get_user(request)
            upload_files_for_related_model(files=files,
                                           related_model=models.Job.objects.get(pk=result.data['id']), who=who)

        return result

    def filter_slab_schedule(self, request, queryset):
        slab_date_start = request.query_params.get('slab_date_start', None)
        slab_date_end = request.query_params.get('slab_date_end', None)

        if slab_date_start:
            print ("Getting Slab Schedule Jobs for %s to %s" % (slab_date_start, slab_date_end))

            date_range = (slab_date_start, slab_date_end)

            queryset = queryset.filter(Q(job_type__code="Slab", date_cancelled__isnull=True), Q(
                Q(pour_date__range=date_range) |
                Q(piers_date__range=date_range)
            ))

        return queryset

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_paving_active(self, request, queryset):
        return queryset.filter(call_up_date__gte=datetime.datetime.now(), date_cancelled__isnull=True,
                               active_end_date__isnull=True).order_by("pour_date")

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_paving_inactive(self, request, queryset):
        return queryset.filter(pour_date__isnull=True)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_all(self, request, queryset):
        return queryset     # NOOP - No filter here.

    def filter_null_pour_date(self, request, queryset):
        return queryset.filter(pour_date__isnull=True)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_inactive2(self, request, queryset):
        # there's another default filter_inactive for OcomViewset that is being run so we make it unique for
        # Cormack instead
        return queryset.filter(Q(date_cancelled__isnull=False) | Q(active_end_date__isnull=False))

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_completed(self, request, queryset):
        return queryset.filter(active_end_date__isnull=False)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_not_called_up(self, request, queryset):
        return queryset.filter(call_up_date__isnull=True)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_not_invoiced(self, request, queryset):
        return queryset.filter(job_costs__invoiced=False, active_end_date__isnull=True).distinct()

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_cancelled(self, request, queryset):
        return queryset.filter(date_cancelled__isnull=False)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_overdue(self, request, queryset):
        return queryset.filter(pour_date__lt=datetime.datetime.now(),
                               date_cancelled__isnull=True, active_end_date__isnull=True)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_called_up(self, request, queryset):
        # we select active records only
        return filter_queryset_by_active_status(queryset.filter(call_up_date__isnull=False))


class RepairViewSet(ActiveCommonViewset):
    queryset = models.Repair.objects.all()
    serializer_class = serializers.RepairSerializer
    filter_backends = (DjangoFilterBackend, FilterFilter, StandardFilter, QueryFilter, SearchFilter, OrderingFilter)
    ordering_fields = ('end_date', 'end_date_notes', 'repair_amount' )
    def get_queryset(self):
        user = self.get_user(self.request)
        queryset = models.Repair.objects.all()

        if user.is_staff or user.is_superuser:
            return queryset
        else:
            role = models.Role.objects.get(user=user)

            if role:
                if role.employee:
                    return queryset

                if role.supervisor:
                    super_main = models.Supervisor.objects.get(user=user)

                    if super_main:
                        queryset = queryset.filter(job__supervisor=super_main)
                    else:
                        queryset = queryset.none()

                if role.client_manager:
                    manager = models.ClientManager.objects.get(user=user)
                    queryset = queryset.filter(job__client=manager.client) if manager else queryset.none()

                if role.subcontractor:
                    subbie = models.Subbie.objects.get(user=user)

                    if subbie:
                        queryset = queryset.filter(repair_subbie=subbie)

                        if not subbie.can_see_plans_before_accept:
                            queryset = queryset.filter(rejected_date__isnull=True)
                    else:
                        queryset = queryset.none()
            else:
                # it not staff/superuser then return nothing as there is no Role
                if not user.is_staff and not user.is_superuser:
                    queryset = queryset.none()

        return queryset

    def filter_active(self, request, queryset):
        return  queryset.filter(Q(completed_date__isnull=True) | Q(completed_date__lt=datetime.datetime.now()))

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_all(self, request, queryset):
        return queryset     # NOOP - No filter here.

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_completed(self, request, queryset):
        return queryset.filter(completed_date__isnull=False)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def filter_overdue(self, request, queryset):
        return queryset.filter(completed_date__isnull=True, due_date__lt=datetime.datetime.now())


class SubbieViewSet(CommonViewset):
    queryset = models.Subbie.objects.all()
    serializer_class = serializers.SubbieSerializer
    filter_backends = (DjangoFilterBackend,)

class SupervisorViewSet(CommonViewset):
    queryset = models.Supervisor.objects.all()
    serializer_class = serializers.SupervisorSerializer
    filter_backends = (DjangoFilterBackend,)


class ClientManagerViewSet(CommonViewset):
    queryset = models.ClientManager.objects.all()
    serializer_class = serializers.ClientManagerSerializer
    filter_backends = (DjangoFilterBackend,)


class UserViewSet(viewsets.ModelViewSet):
    queryset =User.objects.all()
    serializer_class = serializers.UserSerializer


class CodeJobTypeViewSet(OcomModelViewSet):
    queryset = models.CodeJobType.objects.all()
    serializer_class = serializers.CodeJobTypeSerializer


class CodeMixViewSet(OcomModelViewSet):
    queryset = models.CodeMix.objects.all()
    serializer_class = serializers.CodeMixSerializer


class CodePavingColourViewSet(OcomModelViewSet):
    queryset = models.CodePavingColour.objects.all()
    serializer_class = serializers.CodePavingColourSerializer


class CodePavingTypeViewSet(OcomModelViewSet):
    queryset = models.CodePavingType.objects.all()
    serializer_class = serializers.CodePavingTypeSerializer


class CodePurchaseOrderTypeViewSet(OcomModelViewSet):
    queryset = models.CodePurchaseOrderType.objects.all()
    serializer_class = serializers.CodePurchaseOrderTypeSerializer


class CodeDrainTypeViewSet(OcomModelViewSet):
    queryset = models.CodeDrainType.objects.all()
    serializer_class = serializers.CodeDrainTypeSerializer

class CodeDepotTypeViewSet(OcomModelViewSet):
    queryset = models.CodeDepotType.objects.all()
    serializer_class = serializers.CodeDepotTypeSerializer

class CodeSubbieTypeViewSet(OcomModelViewSet):
    queryset = models.CodeSubbieType.objects.all()
    serializer_class = serializers.CodeSubbieTypeSerializer


class CodeFileTypeViewSet(OcomModelViewSet):
    queryset = models.CodeFileType.objects.all()
    serializer_class = serializers.CodeFileTypeSerializer


class CodeRepairTypeViewSet(OcomModelViewSet):
    queryset = models.CodeRepairType.objects.all()
    serializer_class = serializers.CodeRepairTypeSerializer


class CodeTaskTypeViewSet(OcomModelViewSet):
    queryset = models.CodeTaskType.objects.all()
    serializer_class = serializers.CodeTaskTypeSerializer

class CodeTimeOfDayViewSet(OcomModelViewSet):
    queryset = models.CodeTimeOfDay.objects.all()
    serializer_class = serializers.CodeTimeOfDaySerializer


class ClientViewSet(OcomUserRoleMixin, OcomModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer

    def get_queryset(self):
        # check logged-in user
        user = self.get_user(self.request)
        all_fields = self.request.GET.getlist('fieldList')

        try:
            if not user or user.role is None:
                return models.Client.objects.none()
        except ObjectDoesNotExist:
            return models.Client.objects.none()

        return filter_queryset(self.request.query_params, self.queryset, all_fields)


class FileUploadViewSet(OcomUserRoleMixin, viewsets.ModelViewSet):
    queryset = models.FileUpload.objects.all()
    serializer_class = serializers.FileUploadSerializer

    def perform_create(self, serializer):
        file_type_id = self.request.data.get('file_type')
        file_type = models.CodeFileType.objects.get(pk=file_type_id) if file_type_id else None
        serializer.save(
            file=self.request.data.get('file'),
            name=self.request.data.get('name'),
            prefix=self.request.data.get('prefix', ''),
            file_type=file_type,
            who_uploaded=self.get_user(self.request),
        )


class JobCostViewSet(viewsets.ModelViewSet):
    queryset = models.JobCost.objects.all()
    serializer_class = serializers.JobCostSerializer


class JobDrainsViewSet(viewsets.ModelViewSet):
    queryset = models.JobDrains.objects.all()
    serializer_class = serializers.JobDrainsSerializer


class JobNotificationViewSet(viewsets.ModelViewSet):
    queryset = models.JobNotification.objects.all()
    serializer_class = serializers.JobNotificationSerializer


class TaskViewSet(OcomUserRoleMixin,
                  viewsets.mixins.CreateModelMixin,
                  viewsets.mixins.ListModelMixin,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.UpdateModelMixin,
                  viewsets.mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    filter_backends = (DjangoFilterBackend, QueryFilter,)

    def get_queryset(self):
        user = self.get_user(self.request)
        queryset = models.Task.objects.all()

        if user.is_staff or user.is_superuser:
            return queryset
        else:
            role = models.Role.objects.get(user=user)
            if role:
                if role.supervisor:
                    supervisor = models.Supervisor.objects.get(user=user)

                    if supervisor:
                        jobs = models.Job.objects.filter(supervisor=supervisor).values_list('id', flat=True)
                        queryset = models.Task.objects.filter(job__in=jobs)
                    else:
                        queryset = queryset.none()

                if role.subcontractor:
                    subbie = models.Subbie.objects.get(user=user)
                    if subbie:
                        queryset = models.Task.objects.filter(supplier=subbie)
                    else:
                        queryset = queryset.none()

            else:
                # if not staff/superuser then return nothing as there is no Role
                if not user.is_staff and not user.is_superuser:
                    queryset = queryset.none()

        return queryset


class RepairCostViewSet(viewsets.ModelViewSet):
    queryset = models.RepairCost.objects.all()
    serializer_class = serializers.RepairCostSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer


class RoleViewSet(OcomUserRoleMixin, viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_active_status(self.queryset)
        user = self.get_user(self.request)

        if user is not None:
            # TODO SW: Does this CODE return all users if the user us NOT logged in???

            # If the Request has a User then use that ID so we can't get Other peoples roles.
            # assumes the presence of the param means we want our own Data.
            queryset = queryset.filter(user=user)[:1]
        else:
            queryset = queryset.none()

        return queryset


class HashViewSet(viewsets.ModelViewSet):
    queryset = models.Hash.objects.all()
    serializer_class = serializers.HashSerializer

    def get_key(self):
        params = dict()
        params['params'] = self.request.query_params.get('params')
        params['model'] = self.request.query_params.get('model', '')
        params['action'] = self.request.query_params.get('action', '')
        params['user'] = self.request.session.get('user_id', '')
        return models.Hash.get_key_from_json(params)

    def get_queryset(self):
        return models.Hash.objects.filter(key=self.get_key())

    def create(self, request, *args, **kwargs):
        key = self.get_key()
        current_hash = models.Hash.objects.filter(key=key).first()

        if current_hash:
            current_hash.save()
            return response.Response(request.data, status=status.HTTP_304_NOT_MODIFIED)

        # we used to have a _mutable change here to alter request.data and just return super but it may not work on
        # some servers
        data = copy.copy(request.data)
        data['key'] = self.get_key()
        data['model_name'] = request.query_params.get('model', '')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MailMessagesViewSet(OcomUserRoleMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all().prefetch_related('attachments')
    serializer_class = serializers.MailMessagesSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        user = self.get_user(self.request)

        # user has no roles
        if models.Role.user_has_no_role(user):
            return Message.objects.none()

        # noinspection PyUnresolvedReferences
        if user.role.administrator:
            # queryset = self.queryset
            # to speed up process, we need to get the offset and limit
            queryset = self.queryset
        else:
            return Message.objects.none()

        return filter_queryset(self.request.query_params, queryset, ["id", "subject", "message_id", "body"],
                               with_active_date=False)
