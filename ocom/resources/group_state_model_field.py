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

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework import viewsets, permissions
from ocom.shared.filters import FilterFilter, OcomSortFilter
from query.filter.query_filter import QueryFilter
from ocom.viewsets import OcomActiveModelViewMixin


from ocom import models


class GroupStateModelFieldSerializer(WritableNestedModelSerializer):

    class Meta:
        model = models.GroupStateModelField
        fields = ('pk', 'id', 'field_name','deny_read','deny_update',)
        depth = 10


class GroupStateModelFieldViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.GroupStateModelField.objects.all()
    serializer_class = GroupStateModelFieldSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('field_name','deny_read','deny_update',)
    search_fields = ('field_name','deny_read','deny_update',)
    default_filter = 'all'
