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

from ocom.resources.group_state_model import GroupStateModelSerializer

from ocom import models


class GroupStateSerializer(WritableNestedModelSerializer):
    models = GroupStateModelSerializer(many=True, read_only=False, allow_null=True, required=False)

    class Meta:
        model = models.GroupState
        fields = ('pk', 'id', 'state_name','deny','models', 'details')
        depth = 10


class GroupStateViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.GroupState.objects.all()
    serializer_class = GroupStateSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('state_name','deny','models',)
    search_fields = ('state_name','deny','models',)
    default_filter = 'all'
