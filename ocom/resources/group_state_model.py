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

from ocom.resources.group_state_model_field import GroupStateModelFieldSerializer

from ocom import models


class GroupStateModelSerializer(WritableNestedModelSerializer):
    fields = GroupStateModelFieldSerializer(many=True, read_only=False, allow_null=True, required=False)

    class Meta:
        model = models.GroupStateModel
        fields = ('pk', 'id', 'model_name','fields', 'base_uri')
        depth = 10


class GroupStateModelViewSet(OcomActiveModelViewMixin, viewsets.ModelViewSet):
    queryset = models.GroupStateModel.objects.all()
    serializer_class = GroupStateModelSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('model_name','fields', 'base_uri',)
    search_fields = ('model_name','fields', 'base_uri',)
    default_filter = 'all'
