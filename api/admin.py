#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#
from admin_honeypot.admin import LoginAttemptAdmin
from admin_honeypot.models import LoginAttempt
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django import forms as django_forms
from django.http import HttpResponseRedirect, Http404
from logentry_admin.admin import LogEntryAdmin
from rest_framework.authtoken.admin import Token

from ocom import admin as ocom_admin
from . import forms, models, site


ACTIVE_DATE_FIELDS_TUPLE = ('Active Dates', {
    'fields': ('active_start_date', 'active_end_date', )
})
CODE_DESCRIPTION_TUPLE = ('code', 'description', )
CODE_DESCRIPTION_CAN_EMAIL_TUPLE = CODE_DESCRIPTION_TUPLE + ('can_email', 'is_internal')
CLIENT_TUPLE = ('name', 'xero_customer', 'send_invoices', 'required_part_a', 'they_supply_pump',
                'number_of_purchase_orders', )
ACCOUNT_TUPLE = ('enabled', 'username', 'password', 'confirm_password', )
EMAIL_USERNAME_TUPLE = ('email', 'username', )
NAME_TYPE_XERO_SUPPLIER_TUPLE = ('name', 'type', 'xero_supplier', )


class CodeTableAdmin(ocom_admin.NoDeleteMixin, ocom_admin.CodeModelsAdmin):
    list_display = ocom_admin.build_list_property(*CODE_DESCRIPTION_TUPLE, with_list_filter=False)
    list_filter = ocom_admin.build_list_property('code', )
    fieldsets = (
        (None, {'fields': CODE_DESCRIPTION_TUPLE}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    search_fields = CODE_DESCRIPTION_TUPLE


class CodeFileTypeAdmin(CodeTableAdmin):
    list_display = ocom_admin.build_list_property(*CODE_DESCRIPTION_CAN_EMAIL_TUPLE, with_list_filter=False)
    fieldsets = (
        ('Main Info', {'fields': CODE_DESCRIPTION_CAN_EMAIL_TUPLE}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    form = forms.CodeFileTypeForm


class CodeJobTypeAdmin(CodeTableAdmin):
    list_display = ocom_admin.build_list_property(*(CODE_DESCRIPTION_TUPLE + ('colour_actual', )),
                                                  with_list_filter=False)
    fieldsets = (
        ('Main Info', {
            'fields': CODE_DESCRIPTION_TUPLE + ('background_colour', 'foreground_colour', )
        }), ACTIVE_DATE_FIELDS_TUPLE,
    )
    form = forms.CodeJobTypeForm

    # noinspection PyMethodMayBeStatic
    def colour_actual(self, instance):
        return '<span class="color-block" style="background-color: {}; color: {}">TEXT GOES HERE</span>'.\
            format(instance.background_colour, instance.foreground_colour)
    colour_actual.short_description = "Colour"
    colour_actual.allow_tags = True


class CodeRepairTypeAdmin(CodeTableAdmin):
    form = forms.CodeRepairTypeForm


class CodeTaskTypeAdmin(CodeTableAdmin):
    list_display = ocom_admin.build_list_property(*(CODE_DESCRIPTION_TUPLE + ('colour_actual', )),
                                                  with_list_filter=False)
    fieldsets = (
        ('Main Info', {
            'fields': CODE_DESCRIPTION_TUPLE + ('background_colour', 'foreground_colour', 'job_date_field',
                                                'subbie_field', 'job_date_order',)
        }), ACTIVE_DATE_FIELDS_TUPLE,
    )
    form = forms.CodeTaskTypeForm

    # noinspection PyMethodMayBeStatic
    def colour_actual(self, instance):
        return '<span class="color-block" style="background-color: {}; color: {}">TEXT GOES HERE</span>'.\
            format(instance.background_colour, instance.foreground_colour)
    colour_actual.short_description = "Colour"
    colour_actual.allow_tags = True

class CodeMixAdmin(CodeTableAdmin):
    form = forms.CodeMixForm


class CodePurchaseOrderTypeAdmin(CodeTableAdmin):
    form = forms.CodePurchaseOrderTypeForm


class CodePavingTypeAdmin(CodeTableAdmin):
    form = forms.CodePavingTypeForm


class CodePavingColourAdmin(CodeTableAdmin):
    form = forms.CodePavingColourForm


class CodeDrainTypeAdmin(CodeTableAdmin):
    form = forms.CodeDrainTypeForm

class CodeDepotTypeAdmin(CodeTableAdmin):
    list_display = ocom_admin.build_list_property(*(CODE_DESCRIPTION_TUPLE + ('colour_actual', )),
                                                  with_list_filter=False)
    fieldsets = (
        ('Main Info', {
            'fields': CODE_DESCRIPTION_TUPLE + ('background_colour', 'foreground_colour', )
        }), ACTIVE_DATE_FIELDS_TUPLE,
    )
    form = forms.CodeDepotTypeForm

    # noinspection PyMethodMayBeStatic
    def colour_actual(self, instance):
        return '<span class="color-block" style="background-color: {}; color: {}">TEXT GOES HERE</span>'.\
            format(instance.background_colour, instance.foreground_colour)
    colour_actual.short_description = "Colour"
    colour_actual.allow_tags = True

class CodeSubbieTypeAdmin(CodeTableAdmin):
    form = forms.CodeSubbieTypeForm


class CodeTimeOfDayAdmin(CodeTableAdmin):
    form = forms.CodeTimeOfDayForm




class CreateUserAdminMixin(object):
    def save_model(self, request, obj, form, change):
        new_role = None

        if obj.username == '':
            # TODO: either delete account or disable it
            pass
        else:
            if not obj.user:    # Create NEW User
                user = User()
                user.username = obj.username
                user.is_staff = False

                new_role = models.Role()
                # noinspection PyUnresolvedReferences
                setattr(new_role, self.role_name, True)
                new_role.user = user

            else:   # Update existing..
                user = obj.user
                obj.username = user.username    # Make username NOT change.

            # Keep this up to date.
            user.email = obj.email
            user.is_active = obj.enabled

            if obj.password:    # Change password if there is a value here
                user.set_password(obj.password)
                obj.password = ""   # Don't store clear text
                # TODO Should password be a "virtual" field so it's not in the database.
            user.save()

            if new_role is not None:
                new_role.user = user
                new_role.save()

            obj.user = user

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

            user.groups.clear()  # clear for this user.

            # this is where we do some permission set updates
            for item in group_mapping:
                group, _ = Group.objects.get_or_create(name=item['group_name'])

                if getattr(user.role, item['field_name'], False):
                    group.user_set.add(user)
                else:
                    group.user_set.remove(user)

        # noinspection PyUnresolvedReferences
        super(CreateUserAdminMixin, self).save_model(request, obj, form, change)


class SubbieAdmin(CreateUserAdminMixin, ocom_admin.OcomModelAdmin):
    fieldsets = (
        ('Main Info', {'fields': NAME_TYPE_XERO_SUPPLIER_TUPLE + ('email', 'rate_per_m', 'jobs_per_day',
                                                                  'can_see_plans_before_accept', 'display_order',)}),
        ('Account', {'classes': ('collapse',), 'fields': ACCOUNT_TUPLE}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    list_display = ocom_admin.build_list_property(*(('name', 'type', 'has_xero', 'display_order',) +
                                                    EMAIL_USERNAME_TUPLE),
                                                  with_list_filter=False)
    list_filter = ocom_admin.build_list_property('type', 'enabled')
    search_fields = ('name', 'display_order', ) + EMAIL_USERNAME_TUPLE
    form = forms.SubbieForm

    role_name = "subcontractor"

    # noinspection PyMethodMayBeStatic
    def has_xero(self, obj):
        if obj.xero_supplier:
            return "Existing Xero Supplier"
        else:
            return "-- Create New --"


class SupervisorAdmin(CreateUserAdminMixin, ocom_admin.OcomModelAdmin):
    fieldsets = (
        ('Main Info', {'fields': ('name', 'email', 'phone_number', 'client', )}),
        ('Account', {'classes': ('collapse',), 'fields': ACCOUNT_TUPLE}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    list_display = ocom_admin.build_list_property(*('name', 'email', 'phone_number', 'enabled', 'username'),
                                                  with_list_filter=False)
    list_filter = ocom_admin.build_list_property('enabled')
    search_fields = ('name', 'phone_number', ) + EMAIL_USERNAME_TUPLE
    form = forms.SupervisorForm

    role_name = "supervisor"


class ClientManagerAdmin(CreateUserAdminMixin, ocom_admin.OcomModelAdmin):
    fieldsets = (
        ('Main Info', {'fields': ('name', 'email', 'phone_number', 'client', )}),
        ('Account', {'classes': ('collapse',), 'fields': ACCOUNT_TUPLE}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    list_display = ocom_admin.build_list_property(*('name', 'email', 'phone_number', 'enabled', 'username'),
                                                  with_list_filter=False)
    list_filter = ocom_admin.build_list_property('enabled')
    search_fields = ('name', 'phone_number', ) + EMAIL_USERNAME_TUPLE
    form = forms.ClientManagerForm

    role_name = "client_manager"


class ClientAdmin(ocom_admin.OcomModelAdmin):
    fieldsets = (
        ('Main Info', {'fields': CLIENT_TUPLE + ('suppliers', )}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    list_display = ocom_admin.build_list_property(*('name', 'has_xero', 'send_invoices', 'required_part_a',
                                                    'they_supply_pump',), with_list_filter=False)
    list_filter = ocom_admin.build_list_property('suppliers__name')
    search_fields = ('name', 'suppliers__name', )
    form = forms.ClientForm

    # noinspection PyMethodMayBeStatic
    def has_xero(self, obj):
        if obj.xero_customer:
            return "Existing Xero Customer"
        else:
            return "-- Create New --"


#
#   CodeSupplierType
#

class CodeSupplierTypeAdminForm(django_forms.ModelForm):

    class Meta:
        model = models.CodeSupplierType
        fields = ['code', 'description', 'active_start_date', 'active_end_date', ]


class CodeSupplierTypeAdmin(admin.ModelAdmin):
    form = CodeSupplierTypeAdminForm
    list_display = ['description','active_start_date','active_end_date',]
    readonly_fields = [] #TODO


#
#   CodeSupplier
#

class CodeSupplierAdminForm(django_forms.ModelForm):

    class Meta:
        model = models.CodeSupplier
        fields = ['supplier_type', 'code','description', 'active_start_date','active_end_date',]


class CodeSupplierAdmin(admin.ModelAdmin):
    form = CodeSupplierAdminForm
    list_display = ['description', 'supplier_type', 'active_start_date', 'active_end_date',]
    readonly_fields = []    # TODO


class UserAdmin(BaseUserAdmin):
    # def add_view(self, request, form_url='', extra_context=None):
    #     return False

    # noinspection PyShadowingBuiltins
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))

        if user is None:
            raise Http404("User does not exist.")

        if user == request.user:
            # we need to redirect the logged in staff to the password change form with old password
            return HttpResponseRedirect(reverse('admin:password_change'))

        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)

            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                messages.success(request, "Password changed successfully.")
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect('/adm/auth/user')

        return super(UserAdmin, self).user_change_password(request, id, form_url)

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_model(UserAdmin, request, obj):
        pass



# noinspection PyMethodMayBeStatic
class RoleAdmin(ocom_admin.NoDeleteMixin, admin.ModelAdmin):
    fieldsets = (
        ('Main Info', {'fields': ('user', 'is_active', 'first_name', 'last_name', 'email', 'administrator', 'supervisor',
                                  'subcontractor', 'client_manager', 'employee')}),
        ACTIVE_DATE_FIELDS_TUPLE,
    )
    list_display = ocom_admin.build_list_property(
        *('user', 'is_active', 'administrator', 'supervisor', 'subcontractor', 'client_manager',
          'employee', 'last_name', 'first_name', 'email',), with_list_filter=False)
    form = forms.RoleForm
    list_filter = ocom_admin.build_list_property('administrator', 'supervisor', 'subcontractor',
                                                 'client_manager', 'employee')
    search_fields = ('user__last_name', 'user__first_name', 'user__email', 'user__username')
    ordering = ('user__username',)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'

    def last_name(self, obj):
        return obj.user.last_name
    last_name.admin_order_field = 'user__last_name'

    def first_name(self, obj):
        return obj.user.first_name
    first_name.admin_order_field = 'user__first_name'

    def is_active(self, obj):
        return obj.user.is_active
    is_active.short_description = "Is Active"
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True

    def change_password(self, obj):
        # the link here is presumed so if this was customised in urls.py, you have to change the one below as well
        return '<a href="/adm/auth/user/{}/password/">Change</a>'.format(obj.user.id)
    change_password.allow_tags = True
    change_password.short_description = "Password"


admin.site = site.CormackAdminSite()
admin.site.register(models.CodeFileType, CodeFileTypeAdmin)
admin.site.register(models.CodeJobType, CodeJobTypeAdmin)
admin.site.register(models.CodeRepairType, CodeRepairTypeAdmin)
admin.site.register(models.CodeTaskType, CodeTaskTypeAdmin)
admin.site.register(models.CodeMix, CodeMixAdmin)
admin.site.register(models.CodePurchaseOrderType, CodePurchaseOrderTypeAdmin)
admin.site.register(models.CodePavingType, CodePavingTypeAdmin)
admin.site.register(models.CodePavingColour, CodePavingColourAdmin)
admin.site.register(models.CodeDrainType, CodeDrainTypeAdmin)
admin.site.register(models.CodeDepotType, CodeDepotTypeAdmin)
admin.site.register(models.CodeSubbieType, CodeSubbieTypeAdmin)
admin.site.register(models.CodeTimeOfDay, CodeTimeOfDayAdmin)

admin.site.register(models.CodeSupplierType, CodeSupplierTypeAdmin)
admin.site.register(models.CodeSupplier, CodeSupplierAdmin)

admin.site.register(models.Subbie, SubbieAdmin)
admin.site.register(models.Supervisor, SupervisorAdmin)
admin.site.register(models.ClientManager, ClientManagerAdmin)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Role, RoleAdmin)
# we disable delete from list
admin.site.disable_action('delete_selected')
# we disable Group authentication and rely on custom user role management
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.unregister(Token)
admin.site.register(User, UserAdmin)
admin.site.unregister(LogEntry)
admin.site.unregister(LoginAttempt)
admin.site.register(models.Job)


class SecurityAdminSite(AdminSite):
    site_header = "Security Admin"
    site_title = "Hidden Security Admin Portal"
    index_title = ""


event_admin_site = SecurityAdminSite(name='security_admin')
# event_admin_site.register(User, BaseUserAdmin)
event_admin_site.register(Group, GroupAdmin)
event_admin_site.register(User, UserAdmin)
event_admin_site.register(LogEntry, LogEntryAdmin)
event_admin_site.register(LoginAttempt, LoginAttemptAdmin)
