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

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets


'''
This ViewSet and Serializer is to be use to show the "user" of something ie Who Created something. 

It just returns the Descriptive name and the id. No username or Password!

'''
class UserListSerializer(serializers.ModelSerializer):
    descriptive_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'descriptive_name', )
        read_only_fields = ('id', 'descriptive_name')

    # noinspection PyMethodMayBeStatic
    def get_descriptive_name(self, obj):
        """Return the descriptive name of the account by either using the full name, email, or username, in that order
        depending on what fields are empty"""

        result = obj.get_full_name()

        if result == '':
            result = obj.get_username() if obj.email == '' else obj.email

        return result

class UserListViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

