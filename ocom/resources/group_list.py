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
from rest_framework import serializers, viewsets


'''
This ViewSet and Serializer is to be use to show the "Group" of something ie in the Management of the Role Permissions 

It just returns the name and the id.

'''
class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', )
        read_only_fields = ('id', 'name')

class GroupListViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

