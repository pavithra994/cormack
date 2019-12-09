#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_payload_handler as original_jwt_payload_handler
from ocom.role_resource import UserSerializer
from ocom.serializers import TokenUserSerializer
from .auth_override import JSONWebTokenParamAuthentication

def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """

    response = original_jwt_payload_handler(user) # call original

    response['user'] = TokenUserSerializer(user).data # Has NO permissionMap

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
        'user': UserSerializer(user).data, # Has permission Map
        'token': token
    }
