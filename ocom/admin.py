#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.contrib import admin
from ocom.shared.queryset_utils import filter_queryset_by_active_status, filter_queryset_by_inactive_status

import pytz


# noinspection PyAbstractClass
def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


def build_list_property(*args, with_list_filter = True, format_date=False):
    """Create a list property with proper ordering of Active List Filter and Active dates

    Usage:
    from ocom.admin import build_list_property

    class SomeModelAdmin(admin.ModelAdmin):
        list_display = build_list_property('name', 'code', 'description', with_list_filter=False)
        # is equivalent to list_display = ('name', 'code', 'description', 'active_start_date', 'active_end_date')
        list_filter = build_list_property('item', 'sub_item')
        # is equivalent to list_filter = (ActiveListFilter, 'item', 'sub_item', 'active_start_date', 'active_end_date')

    :param bool with_list_filter: if True, adds ActiveListFilter as the first entry to the list
    :param bool format_date: if True, formats date based on settings.DATETIME_FORMAT
    :param args: a series of args to add onto list filter
    :return: the modified list filter
    """

    whitelist = ['active_start_date', 'active_end_date', 'start_date', 'end_date']
    base_list = ()

    for arg in args:
        if arg not in whitelist:
            base_list += tuple([arg])

    if with_list_filter:
        base_list += (ActiveListFilter,)

    base_list += ('start_date', 'end_date',) if format_date else ('active_start_date', 'active_end_date',)
    return base_list


class ActiveListFilter(admin.SimpleListFilter):
    """
    Filter for Active dates

    Usage:
    from ocom.admin import ActiveListFilter
    class EmployeeAdmin(admin.ModelAdmin):
        search_fields = ('code', 'name',)
        list_display = ('code', 'name', 'active_start_date', 'active_end_date')
        list_filter = (ActiveListFilter,)
    """

    title = "Active Status"
    parameter_name = 'active_start_date'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('all', 'All')
        )

    def queryset(self, request, queryset):
        if self.value() == 'active' or self.value() is None:
            return filter_queryset_by_active_status(queryset)

        if self.value() == 'inactive':
            return filter_queryset_by_inactive_status(queryset)


class CodeModelsAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'active_start_date', 'active_end_date', )


class CommonFilterMixin(object):
    """Common filter mixin which includes 'active_start_date' and 'active_end_date' in it's list_filter

    Usage:
    from ocom.admin import CommonFilterMixin

    class SomeModelAdmin(CommonFilterMixin, admin.ModelAdmin):
        def some_function(self):
            print(self.list_filter)
            # ('active_start_date', 'active_end_date')
            ...
    """

    list_filter = build_list_property()


class CommonSortFilterMixin(CommonFilterMixin):
    """Variation of Common filter mixin with sortable set to 'name' and search_fields with 'name' as default

    Usage:
    from ocom.admin import CommonSortFilterMixin

    class SomeModelAdmin(CommonSortFilterMixin, admin.ModelAdmin):
        def some_function(self):
            print(self.list_filter, self.sortable, self.search_fields)
            # ('active_start_date', 'active_end_date') name ('name',)
            ...
    """

    sortable = 'name'
    search_fields = ('name',)


class NoDeleteMixin(object):
    """Mixin which removes and restricts 'hard' delete links

    Usage:
    from ocom.admin import NoDeleteMixin, CommonSortFilterMixin

    # Example 1
    class SomeModelAdmin(NoDeleteMixin, admin.ModelAdmin):
        def some_function(self):
            ...

    # Example 2 (used in conjunction with CommonSortFilterMixin
    class SomeModelAdmin(NoDeleteMixin, CommonSortFilterMixin, admin.ModelAdmin):
        def some_function(self):
            ...
    """

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def has_delete_permission(self, request, obj=None):
        # disable delete link
        return False


class ReadOnlyModelAdmin(NoDeleteMixin, admin.ModelAdmin):
    """Variation of no delete mixin which sets all fields to read only. Particularly useful for admin logs

    Usage:
    from ocom.admin import ReadOnlyModelAdmin

    class SomeModelAdmin(ReadOnlyModelAdmin, admin.ModelAdmin):
        def some_function(self):
            ...
    """

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def has_add_permission(self, request, obj=None):
        # disable add
        return False

    def has_change_permission(self, request, obj=None):
        # allow view but prohibit saving edits
        return request.method in ['GET', 'HEAD'] and super().has_change_permission(request, obj)


class OcomModelAdmin(NoDeleteMixin, CommonSortFilterMixin, admin.ModelAdmin):
    # noinspection PyMethodMayBeStatic
    def start_date(self, instance):
        if instance.active_start_date is None:
            return '-'

        if settings.USE_TZ and settings.TIME_ZONE != 'UTC':
            local_timezone = pytz.timezone(settings.TIME_ZONE)
            return instance.active_start_date.astimezone(local_timezone).strftime(settings.DATETIME_FORMAT)
        else:
            return instance.active_start_date.strftime(settings.DATETIME_FORMAT)

    start_date.short_description = "Active Start Date"
    start_date.admin_order_field = 'active_start_date'

    # noinspection PyMethodMayBeStatic
    def end_date(self, instance):
        if instance.active_end_date is None:
            return '-'

        if settings.USE_TZ and settings.TIME_ZONE != 'UTC':
            local_timezone = pytz.timezone(settings.TIME_ZONE)
            return instance.active_end_date.astimezone(local_timezone).strftime(settings.DATETIME_FORMAT)
        else:
            return instance.active_end_date.strftime(settings.DATETIME_FORMAT)

    end_date.short_description = "Active End Date"
    end_date.admin_order_field = 'active_end_date'
