#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField

from rest_framework import viewsets, permissions
from rest_framework import filters

from ocom.shared.filters import FilterFilter
from ocom.viewsets import OcomActiveModelViewMixin

from query import models

class QueryDefSerializer(WritableNestedModelSerializer):

    class Meta:
        model = models.QueryDef
        fields = ('pk', 'id', 'modified_date','created_date','active_start_date','active_end_date','name','filter','model_name',)
        depth = 10


class QueryDefViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.QueryDef.objects.all()
    serializer_class = QueryDefSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, FilterFilter,)
    ordering_fields = ('modified_date','created_date','active_start_date','active_end_date','name','filter','model_name',)
    search_fields = ('modified_date','created_date','active_start_date','active_end_date','name','filter','model_name',)


    default_filter = 'all'
