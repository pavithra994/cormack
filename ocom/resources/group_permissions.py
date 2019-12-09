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

from django.contrib.auth.models import Group
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework import viewsets, permissions
from ocom.shared.filters import FilterFilter, OcomSortFilter
from query.filter.query_filter import QueryFilter
from ocom.viewsets import OcomActiveModelViewMixin

from ocom.resources.group_state import GroupStateSerializer

from ocom import models


class GroupPermissionsSerializer(WritableNestedModelSerializer):
    group = PrimaryKeyRelatedField(many=False, read_only=False, allow_null=False, queryset=Group.objects.all())
    states = GroupStateSerializer(many=True, read_only=False, allow_null=True, required=False)

    class Meta:
        model = models.GroupPermissions
        fields = ('pk', 'id', 'group','states', 'details')
        depth = 10


class GroupPermissionsViewSet(viewsets.ModelViewSet):
    queryset = models.GroupPermissions.objects.all()
    serializer_class = GroupPermissionsSerializer
    permission_classes = [permissions.IsAuthenticated] #TODO
    filter_backends = (QueryFilter, FilterFilter, OcomSortFilter)
    ordering_fields = ('group','states',)
    search_fields = ('group','states',)
    default_filter = 'all'
