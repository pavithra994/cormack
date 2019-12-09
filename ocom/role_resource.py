#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

# Default Role serializer and viewset to use if Role model is not used / required

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework import serializers, viewsets
from rest_framework.response import Response

from ocom.utils.permission import calculatePermissionMap


class Role(object):
    def __init__(self, **kwargs):
        for field in ('id', 'administrator', 'role_name1', 'role_name2', 'role_name3', 'user_id'):
            setattr(self, field, kwargs.get(field, None))


# sample roles
roles = {
    1: Role(id=1, administrator=True, role_name1=False, role_name2=False, role_name3=False, user_id=1),
    2: Role(id=2, administrator=False, role_name1=True, role_name2=False, role_name3=False, user_id=2),
    3: Role(id=3, administrator=False, role_name1=False, role_name2=True, role_name3=False, user_id=3),
    4: Role(id=4, administrator=False, role_name1=False, role_name2=False, role_name3=True, user_id=4),
}


class RoleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    administrator = serializers.BooleanField(default=False)
    role_name1 = serializers.BooleanField(default=False)
    role_name2 = serializers.BooleanField(default=False)
    role_name3 = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return Role(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        return instance

    class Meta:
        model = Role
        fields = ('id', 'administrator', 'role_name1', 'role_name2', 'role_name3', 'user_id')


class RoleViewSet(viewsets.ViewSet):
    serializer_class = RoleSerializer

    def list(self, request):
        serializer = RoleSerializer(instance=roles.values(), many=True)
        return Response(serializer.data)


# use this class only when you are not using a Role model, otherwise use the one at ocom.serializers
class UserSerializer(serializers.ModelSerializer):
    # role = RoleSerializer(required=False, allow_null=True)
    role = serializers.SerializerMethodField()
    descriptive_name = serializers.SerializerMethodField()
    _permissionMap = serializers.SerializerMethodField()

    def get_role(self, instance):
        # iterate through each one and find the user_id to link with User object
        for found_role in roles.values():
            # get the first match only
            if found_role.__dict__['user_id'] == instance.id:
                return found_role.__dict__

        return None

    def get_descriptive_name(self, instance):
        """Return the descriptive name of the account by either using the full name, email, or username, in that order
        depending on what fields are empty"""

        result = instance.get_full_name()

        if result == '':
            result = instance.get_username() if instance.email == '' else instance.email

        return result

    def get_fields(self):
        """
        Returns a dictionary of {field_name: field_instance}.
        """
        # Every new serializer is created with a clone of the field instances.
        # This allows users to dynamically modify the fields on a serializer
        # instance without affecting every other serializer class.
        fields = super(UserSerializer, self).get_fields()
        return fields

    # noinspection PyMethodMayBeStatic
    def get__permissionMap(self, obj):
        return calculatePermissionMap (obj)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions',
                  'is_active', 'last_login', 'date_joined', 'is_staff', 'descriptive_name', 'role', '_permissionMap')
        depth = 2
