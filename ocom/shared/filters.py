#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

#
#
#

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from ocom.shared.queryset_utils import filter_queryset_by_active_status
from ocom.utils.drf_views_snippets import filter_queryset ,sort_queryset


class CodeModelFilter(BaseFilterBackend):
    """
    Filter the CodeModel. This is a generic filter for this sort of Model.
    """

    def filter_queryset(self, request, queryset, view):
        modified_date = request.query_params.get('modified_date', None)

        if modified_date:
            queryset = queryset.filter(modified_date__date__gte=modified_date[:10])

        return queryset


class ActiveFilter(BaseFilterBackend):
    """
    Filter the model on Active Status
    """

    def filter_queryset(self, request, queryset, view):
        queryset = filter_queryset_by_active_status(queryset)

        return queryset


class FilterFilter(BaseFilterBackend):
    """
    Takes a filter parameter in the request and uses that to call a method
    with the prefix "filter_" in the view

    For example if the request has a param filter=all then we will expect to find in the view
    a method like

        def filter_all (self, request, queryset):
            return queryset
    """

    def filter_queryset(self, request, queryset, view):
        filter_name = request.query_params.get('filter', None)

        if filter_name is None:
            filter_name = getattr(view, "default_filter", None)

        if filter_name is not None:
            filter_method = getattr(view, "filter_" + filter_name, None)

            if callable(filter_method):
                queryset = filter_method(request, queryset)

        return queryset


class OcomSearchFilter (BaseFilterBackend):
    """Useful in ModelViewSets for filtering querysets based on params received from the client (angular).

                A typical Ocom App List Page (http://ocom.com.au/lookbook/code/list.html) would have
                    - Filters: q, searchField

                Sample Usage:
                from ocom.utils.drf_snippets import filter_queryset
                class CompanyRateModelViewSet(OcomModelViewSet):
                    filter_backends = (OcomSearchFilter,)
                    q_search_fields= ['id', 'name', 'some_other_char_field', 'realated__charfield'] # the field we can search

                """

    def filter_queryset(self, request, queryset, view):
        q = request.query_params.get('q', None)
        search_field = request.query_params.get('searchField', None)

        if q:
            if search_field:
                if view.q_search_fields is not None:
                    if search_field not in view.q_search_fields:
                        raise ValueError("Cannot find field " + search_field + " in list of fields")

                search_field = search_field + "__icontains"
                queryset = queryset.filter(**{search_field: q})

            else:  # Search all CharFields
                if view.q_search_fields:
                    if len(view.q_search_fields) == 1:
                        queryset = queryset.filter(id__startswith=q) \
                            if view.q_search_fields[0] == 'id' else queryset.filter(id__icontains=q)
                    else:
                        q_objects = Q()  # Create an empty Q object to start with

                        for field in view.q_search_fields:
                            q_objects |= Q(**{"id__startswith": q}) if field == 'id' else Q(
                                **{field + "__icontains": q})
                            # 'or' the Q objects together

                        queryset = queryset.filter(q_objects)

        return queryset

class OcomStandardFilter(BaseFilterBackend):
    """
    This is a standard filter with active dates taken into consideration
    """

    def filter_queryset(self, request, queryset, view):
        return filter_queryset(request.query_params, queryset)


class OcomSortFilter(BaseFilterBackend):
    """
    This is a standard filter with sorting included
    """

    def filter_queryset(self, request, queryset, view):
        return sort_queryset(request.query_params, queryset)


class OcomDistinctFilter(BaseFilterBackend):
    """
    This is a distinct filter for use whenever results from queries mixed with ManyToMany records produce duplicates
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.distinct()
