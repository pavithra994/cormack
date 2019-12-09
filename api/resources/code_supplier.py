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

from api.resources.code_supplier_type import CodeSupplierTypeSerializer
from ocom.shared.filters import FilterFilter, OcomSortFilter
from query.filter.query_filter import QueryFilter
from ocom.viewsets import OcomActiveModelViewMixin


from api import models


class CodeSupplierSerializer(WritableNestedModelSerializer):
    supplier_type = CodeSupplierTypeSerializer(many=False, read_only=False, allow_null=True)

    class Meta:
        model = models.CodeSupplier
        fields = ('pk', 'id', 'code','description','active_start_date','active_end_date','created_date','modified_date','supplier_type',)
        depth = 10


class CodeSupplierViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.CodeSupplier.objects.all()
    serializer_class = CodeSupplierSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('code','description','active_start_date','active_end_date','created_date','modified_date','supplier_type',)
    search_fields = ('code','description','active_start_date','active_end_date','created_date','modified_date','supplier_type',)
    default_filter = 'all'
