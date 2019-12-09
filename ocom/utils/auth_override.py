#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication, JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_payload_handler as original_jwt_payload_handler

from ocom.serializers import UserSerializer, TokenUserSerializer
from datetime import datetime
from calendar import timegm
from rest_framework_jwt.settings import api_settings

def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """

    response = original_jwt_payload_handler(user) # call original

    response['user'] = TokenUserSerializer(user).data # has not 'permissionMap'

    return response

def jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user).data
        }

    """
    return {
        'user': UserSerializer(user).data, # has 'PermissionMap'
        'token': token
    }

# From http://getblimp.github.io/django-rest-framework-jwt/#extending-jsonwebtokenauthentication
class JSONWebTokenParamAuthentication(JSONWebTokenAuthentication):
    """
    Use this class in the APIView as a permission class ie
    authentication_classes = (JSONWebTokenParamAuthentication,)

    or on a APIView function
    @authentication_classes((JSONWebTokenParamAuthentication,))

    When included, the jwt token can be specified in the jwt parameter instead of the header.
    """

    def get_jwt_value(self, request):
        return request.query_params.get('jwt') or JSONWebTokenAuthentication.get_jwt_value(self, request)
