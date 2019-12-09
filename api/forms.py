#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth.models import User, Group
# from django.contrib.auth.hashers import make_password
from django.db.models import ManyToOneRel
# from ocom.shared.queryset_utils import filter_queryset_by_active_status
from django.forms import TextInput

from ocom_xero.admin_utils import get_supplier_choices, get_customer_choices
from . import models

ACTIVE_DATES_TUPLE = ('active_start_date', 'active_end_date', )
CODE_TUPLE = ('code', 'description',)
MIN_PASSWORD_LENGTH = 6


def check_filter_set_duplicate_count(model, filter_set):
    """Return count of duplicate filter set

    :param model: the model instance
    :param dict filter_set: the duplicate check filter to apply
    :return: True if duplicate exists
    :rtype: bool
    """

    try:
        # noinspection PyProtectedMember
        return model._meta.default_manager.filter(**filter_set).count()
    except (model.DoesNotExist, ):
        return 0


def validate_active_end_date(cleaned_data):
    """Return status of active_end_date if it is set before active_start_date
    :param dict cleaned_data: the current / cleaned data
    :return: True if active_end_date is greater than active_start_date
    :rtype: bool
    """

    start_date = cleaned_data.get('active_start_date')
    end_date = cleaned_data.get('active_end_date')

    if end_date:
        return end_date > start_date
    else:
        # allow blank active end date
        return True


def validate_password(password, confirm_password):
    return password == confirm_password


class DuplicateFieldEndDateCheckForm(forms.ModelForm):
    """Form class with duplicate checking for a given field list and Active End Date validation"""
    duplicate_skip_empty = []

    def check_duplicates(self, field_list, cleaned_data):
        for field in field_list:
            filter_set = {}
            duplicate_entry = True

            if isinstance(field, (list, tuple)):
                for subfield in field:
                    if subfield in cleaned_data:
                        value = cleaned_data[subfield].id if hasattr(cleaned_data[subfield], 'id') \
                            else cleaned_data.get(subfield)
                    else:
                        value = ''

                    if value or subfield in self.duplicate_skip_empty:
                        filter_set[subfield] = value

                        if self.initial and self.initial.get(subfield) != value:
                            duplicate_entry = False

                if filter_set:
                    duplicates = check_filter_set_duplicate_count(self.instance, filter_set)

                    if (duplicate_entry and duplicates > 1) or (not duplicate_entry and duplicates):
                        for subfield in field:
                            self.add_error(subfield,
                                           "An existing entry with the field{}: {} already matches input.".format(
                                               '' if len(field) == 1 else 's', field))
            else:
                if field in cleaned_data:
                    value = cleaned_data[field].id if hasattr(cleaned_data[field], 'id') \
                        else cleaned_data.get(field)
                else:
                    value = ''

                if value or field in self.duplicate_skip_empty:
                    filter_set[field] = value

                    if self.initial and self.initial.get(field) != value:
                        duplicate_entry = False

                    duplicates = check_filter_set_duplicate_count(self.instance, filter_set)

                    if (duplicate_entry and duplicates > 1) or (not duplicate_entry and duplicates):
                        self.add_error(field, 'An entry with that {} already exists.'.format(field))

    def clean(self):
        cleaned_data = super(DuplicateFieldEndDateCheckForm, self).clean()
        self.check_duplicates(self.duplicate_check_fields, cleaned_data)

        if not validate_active_end_date(cleaned_data):
            self.add_error('active_end_date', 'Active End Date must be blank or greater than Active Start Date.')

        return cleaned_data


class NameForm(DuplicateFieldEndDateCheckForm):
    name = forms.CharField(label='Name', required=True)
    duplicate_check_fields = ['name']


class NameWithPasswordForm(NameForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean_email(self):
        return self.cleaned_data['email'] or None

    def clean_username(self):
        # check if username is already set in another account
        if self.cleaned_data['username'] != '':
            supervisors = models.Supervisor.objects.filter(username=self.cleaned_data['username'])
            subbies = models.Subbie.objects.filter(username=self.cleaned_data['username'])
            model_name = self.instance.__class__.__name__

            if model_name == 'Subbie':
                subbies = subbies.exclude(id=self.instance.pk)

            if model_name == 'Supervisor':
                supervisors = supervisors.exclude(id=self.instance.pk)

            if len(subbies) or len(supervisors):
                self.add_error('username', "Username is already used. Please use another.")

        try:
            return self.cleaned_data['username']
        except KeyError:
            return None

    def clean(self):
        cleaned_data = super(NameWithPasswordForm, self).clean()

        # check if passwords are set
        if cleaned_data['password'] != '' or cleaned_data['confirm_password'] != '':
            if validate_password(cleaned_data['password'], cleaned_data['confirm_password']):
                # cleaned_data['password'] = make_password(cleaned_data['password'])
                if len(cleaned_data['password']) < MIN_PASSWORD_LENGTH:
                    self.add_error('password',
                                   "Your password must have at least {} characters.".format(MIN_PASSWORD_LENGTH))
            else:
                self.add_error('password', "Your password entries do not match.")
                self.add_error('confirm_password', "Your password entries do not match.")

        return cleaned_data


class BaseCodeForm(DuplicateFieldEndDateCheckForm):
    code = forms.CharField(label='Code', required=True)
    duplicate_check_fields = ['code', 'description']

    class Meta:
        abstract = True


class CodeFileTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeFileType
        fields = CODE_TUPLE + ('can_email', ) + ACTIVE_DATES_TUPLE


class CodeJobTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeJobType
        fields = CODE_TUPLE + ('background_colour', 'foreground_colour', ) + ACTIVE_DATES_TUPLE
        widgets = {
            'background_colour': TextInput(attrs={'type': 'color'}),
            'foreground_colour': TextInput(attrs={'type': 'color'})
        }


class CodeRepairTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeRepairType
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodeMixForm(BaseCodeForm):
    class Meta:
        model = models.CodeMix
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodePurchaseOrderTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodePurchaseOrderType
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodeTaskTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeTaskType
        fields = CODE_TUPLE + ('background_colour', 'foreground_colour', 'job_date_field') + ACTIVE_DATES_TUPLE
        widgets = {
            'background_colour': TextInput(attrs={'type': 'color'}),
            'foreground_colour': TextInput(attrs={'type': 'color'})
        }


class CodePavingTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodePavingType
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodePavingColourForm(BaseCodeForm):
    class Meta:
        model = models.CodePavingColour
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodeDrainTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeDrainType
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE

class CodeDepotTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeDepotType
        fields = CODE_TUPLE + ('background_colour', 'foreground_colour', ) + ACTIVE_DATES_TUPLE
        widgets = {
            'background_colour': TextInput(attrs={'type': 'color'}),
            'foreground_colour': TextInput(attrs={'type': 'color'})
        }

class CodeSubbieTypeForm(BaseCodeForm):
    class Meta:
        model = models.CodeSubbieType
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class CodeTimeOfDayForm(BaseCodeForm):
    class Meta:
        model = models.CodeTimeOfDay
        fields = CODE_TUPLE + ACTIVE_DATES_TUPLE


class SubbieForm(NameWithPasswordForm):
    duplicate_check_fields = [['username', 'name']]
    type = forms.ModelChoiceField(label='Subbie Type', queryset=models.CodeSubbieType.objects.all(), required=False)
    xero_supplier = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = models.Subbie
        fields = ('name', 'type', 'xero_supplier', 'rate_per_m', 'jobs_per_day', 'can_see_plans_before_accept',
                  'display_order',
                  'username', 'password', 'confirm_password', 'email', 'enabled') + ACTIVE_DATES_TUPLE

    def __init__(self, *args, **kwargs):
        super(SubbieForm, self).__init__(*args, **kwargs)

        self.fields['xero_supplier'] = forms.ChoiceField(choices=get_supplier_choices(), required=False)


class SupervisorForm(NameWithPasswordForm):
    duplicate_check_fields = [['username', 'name']]

    class Meta:
        model = models.Supervisor
        fields = ('name', 'username', 'password', 'confirm_password', 'email', 'enabled', 'phone_number',
                  'client') + ACTIVE_DATES_TUPLE

class ClientManagerForm(NameWithPasswordForm):
    duplicate_check_fields = [['username', 'name']]

    class Meta:
        model = models.ClientManager
        fields = ('name', 'username', 'password', 'confirm_password', 'email', 'enabled', 'phone_number',
                  'client') + ACTIVE_DATES_TUPLE


class ClientForm(NameForm):
    xero_customer = forms.ChoiceField(choices=[], required=False)

    duplicate_check_fields = [['name', 'xero_customer']]

    class Meta:
        model = models.Client
        fields = ('name', 'xero_customer', 'send_invoices', 'suppliers', 'required_part_a',
                  'they_supply_pump',) + ACTIVE_DATES_TUPLE

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['suppliers'].queryset = models.Subbie.objects.all().order_by('name')
        self.fields['xero_customer'] = forms.ChoiceField(choices=get_customer_choices(), required=False)


class RoleForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all()) 
    first_name = forms.CharField(label='First Name', required=False)
    last_name = forms.CharField(label='Last Name', required=False)
    email = forms.EmailField(label='Email', required=False)
    is_active = forms.BooleanField(label='Is Active', required=False)
    user_selected = forms.CharField(label='User', required=False,
                                    widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = models.Role
        fields = ('user', 'is_active', 'user_selected', 'first_name', 'last_name', 'email', 'administrator',
                  'supervisor', 'subcontractor', 'client_manager') + ACTIVE_DATES_TUPLE

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)

        if self.instance.pk is None:
            unassigned_users = models.Role.objects.filter(user_id__isnull=False).values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=unassigned_users)
            # noinspection PyProtectedMember
            relation = ManyToOneRel(User._meta.get_field('id'), User, 'id')
            self.fields['user'].widget = RelatedFieldWidgetWrapper(self.fields['user'].widget, relation, admin.site)
            self.fields['user_selected'].widget = forms.HiddenInput()
        else:
            self.fields['user'].widget = forms.HiddenInput()
            self.fields['user_selected'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['is_active'].initial = self.instance.user.is_active

    def clean(self):
        cleaned_data = super(RoleForm, self).clean()
        # some additional validation to be done here
        return cleaned_data

    def save(self, commit=True):
        user_update = False

        # update User name / email
        for user_field in ['last_name', 'first_name', 'email', 'is_active']:
            if user_field in self.changed_data:
                setattr(self.cleaned_data['user'], user_field, self.cleaned_data[user_field])

                if not user_update:
                    user_update = True

        if user_update:
            self.cleaned_data['user'].save()

        group_mapping = [
            {
                'field_name': 'supervisor',
                'group_name': 'Supervisor'
            },
            {
                'field_name': 'administrator',
                'group_name': 'Administrator'
            },
            {
                'field_name': 'subcontractor',
                'group_name': 'Subcontractor'
            },
            {
                'field_name': 'client_manager',
                'group_name': 'ClientManager'
            },
            {
                'field_name': 'employee',
                'group_name': 'Employee'
            }
        ]

        # this is where we do some permission set updates
        for item in group_mapping:
            if item['field_name'] in self.changed_data:
                group, _ = Group.objects.get_or_create(name=item['group_name'])

                if self.cleaned_data[item['field_name']]:
                    group.user_set.add(self.cleaned_data['user'])
                else:
                    group.user_set.remove(self.cleaned_data['user'])

        return super(RoleForm, self).save(commit)
