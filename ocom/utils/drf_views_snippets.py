#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.core.exceptions import FieldError
from django.db.models import Q, Model
from ocom.shared.queryset_utils import filter_queryset_by_active_status, filter_queryset_by_inactive_status


def delete_missing_model_items(instance, field, new_items):
    """
    Used in updating forms. When updating the database, the deleted rows in the forms should
    be deleted in the database as well. The dev may opt to automatically delete item when row is deleted in UI.

    Usage:
    class ShiftSerializer(serializers.ModelSerializer):
        class Meta:
            model = Shift
            fields = '__all__'

        def update(self, instance, validated_data):
            loads = validated_data.pop('loads', [])
            delete_missing_model_items(instance, 'loads', loads)

    """

    items_in_database = instance[field].all()

    for item in items_in_database:
        if item.id not in [new.get('id') for new in new_items]:
            item.delete()


def sort_queryset(params, queryset):
    """
    Sort queryset based on field
    :param dict params: the parameters to check for sorting
    :param queryset: the queryset to perform sort operation on
    :return: the sorted queryset

    Sample Usage:
    from ocom.utils.drf_snippets import sort_queryset
    class CompanyRateModelViewSet(OcomModelViewSet):
        def get_queryset(self):
            queryset = CompanyRate.objects.all()
            queryset = sort_queryset(self.request.query_params, queryset)
            return queryset
    """

    sort_field = params.get('sort', None)
    order = params.get('order', None)

    if sort_field:
        if order == 'desc':
            sort_field = '-' + sort_field

        try:
            return queryset.order_by(sort_field)
        except (FieldError, SyntaxError):
            return Model.objects.none()

    return queryset


def filter_queryset(params, queryset, all_fields=None, with_active_date=True):
    """Useful in ModelViewSets for filtering querysets based on params received from the client (angular).

    A typical Ocom App List Page (http://ocom.com.au/lookbook/code/list.html) would have
        - Filters: q, searchField, filter (Active / Not Active / All)
        - Pagination: offset, limit
        - Sorting: sort (sort by model), order (asc/desc)

    Sample Usage:
    from ocom.utils.drf_snippets import filter_queryset
    class CompanyRateModelViewSet(OcomModelViewSet):
        def get_queryset(self):
            queryset = CompanyRate.objects.all()
            queryset = filter_queryset(self.request.query_params, queryset)
            return queryset

    Defaults:
    - Filtering will be 'active' by default.
    """

    q = params.get('q', None)
    search_field = params.get('searchField', None)
    queryset_filter = params.get('filter', None)
    # offset = params.get('offset', None)
    # limit = params.get('limit', None)

    if q:
        if search_field:
            if all_fields is not None:
                if search_field not in all_fields:
                    raise ValueError("Cannot find field " + search_field + " in list of fields")

            search_field = search_field + "__icontains"
            queryset = queryset.filter(**{search_field: q})

        else:  # Search all CharFields
            if all_fields:
                if len(all_fields) == 1:
                    queryset = queryset.filter(id__startswith=q) \
                        if all_fields[0] == 'id' else queryset.filter(id__icontains=q)
                else:
                    q_objects = Q()  # Create an empty Q object to start with

                    for field in all_fields:
                        q_objects |= Q(**{"id__startswith": q}) if field == 'id' else Q(**{field + "__icontains": q})
                        # 'or' the Q objects together

                    queryset = queryset.filter(q_objects)

    if with_active_date or queryset_filter in ('active', 'inactive'):
        queryset = filter_queryset_by_active_status(queryset) if queryset_filter != 'inactive' else \
            filter_queryset_by_inactive_status(queryset)

    return sort_queryset(params, queryset)
