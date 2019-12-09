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
from ocom.shared.filters import FilterFilter, OcomSortFilter
from query.filter.query_filter import QueryFilter
from ocom.viewsets import OcomActiveModelViewMixin


from api import models


class JobSupplySerializer(WritableNestedModelSerializer):
    supplier_type = PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, queryset=models.CodeSupplierType.objects.all())
    supplier = PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, queryset=models.CodeSupplier.objects.all())
    book_time = PrimaryKeyRelatedField(many=False, read_only=False, allow_null=True, queryset=models.CodeTimeOfDay.objects.all())

    class Meta:
        model = models.JobSupply
        fields = ('pk', 'id', 'supplier_type','supplier','book_date','book_time','booking_number',)
        depth = 10


class JobSupplyViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.JobSupply.objects.all()
    serializer_class = JobSupplySerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('supplier_type','supplier','book_date','book_time','booking_number',)
    search_fields = ('supplier_type','supplier','book_date','book_time','booking_number',)
    default_filter = 'all'
