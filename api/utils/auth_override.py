#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from rest_framework import serializers
from api.serializers import RoleSerializer, UserSerializer, User
from rest_framework_jwt.utils import jwt_payload_handler as original_jwt_payload_handler
from ocom.serializers import UserSerializer as BaseUserSerializer

class TokenUserSerializer(BaseUserSerializer):
    role = RoleSerializer()

    class Meta:
        model = User
        # NO _permissionMap as this makes the token HUGE
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions',
                  'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'descriptive_name', 'role',)
        depth = 1       # apparently adds Role to relationships in User model


"""
Derive from ocom.utils.auth_override.py (Use custom serializer)
"""


def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """

    response = original_jwt_payload_handler(user) # call original

    response['user'] = TokenUserSerializer(user).data #Don't put 'permissionMap' in token othterwise it's too long

    return response

# noinspection PyUnusedLocal
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'user': UserSerializer(user).data, # has 'permissionMap'
        'token': token
    }
