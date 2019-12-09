#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

import pytz

from ocom.utils.permission import calculatePermissionMap


def timezone_formatted_datetime(datetime_field):
    """
    Returns a date time field into a string-formatted date time based on timezone from settings.py
    :param datetime_field: the datetime field to convert
    :return: the converted datetime field
    :rtype: str
    """

    return datetime_field.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(settings.DATETIME_FORMAT)


class ActiveDateSerializerMixin(object):
    active_start_date = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=True)
    active_end_date = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=False)


class UserSerializer(serializers.ModelSerializer):
    descriptive_name = serializers.SerializerMethodField()
    _permissionMap = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions',
                  'is_active', 'last_login', 'date_joined', 'is_staff', 'is_superuser', 'descriptive_name')
        depth = 2

    # noinspection PyMethodMayBeStatic
    def get__permissionMap(self, obj):
        return calculatePermissionMap (obj)

    # noinspection PyMethodMayBeStatic
    def get_descriptive_name(self, obj):
        """Return the descriptive name of the account by either using the full name, email, or username, in that order
        depending on what fields are empty"""

        result = obj.get_full_name()

        if result == '':
            result = obj.get_username() if obj.email == '' else obj.email

        return result

class TokenUserSerializer(serializers.ModelSerializer):
    descriptive_name = serializers.SerializerMethodField()
    # _permissionMap = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions',
                  'is_active', 'last_login', 'date_joined', 'is_staff', 'is_superuser', 'descriptive_name')
        depth = 2

    # noinspection PyMethodMayBeStatic
    # def get__permissionMap(self, obj):
    #     return calculatePermissionMap (obj)

    # noinspection PyMethodMayBeStatic
    def get_descriptive_name(self, obj):
        """Return the descriptive name of the account by either using the full name, email, or username, in that order
        depending on what fields are empty"""

        result = obj.get_full_name()

        if result == '':
            result = obj.get_username() if obj.email == '' else obj.email

        return result
