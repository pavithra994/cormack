#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import os
import json
import raven

from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponse
from rest_framework import routers
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token

from ocom.resources.group_list import GroupListViewSet
from ocom.resources.group_permissions import GroupPermissionsViewSet
from ocom.resources.user_list import UserListViewSet
from ocom.views import ScreenShotView, home
from .views import RefreshJSONWebToken, ObtainJSONWebToken, Unauthenticate

admin.autodiscover()


# noinspection PyUnusedLocal
def docker_status(request):
    """
    Return the status of OK for Docker so it's knows the app is UP and running

    :param request: RequestContext object
    :return: HttpResponse
    """

    return HttpResponse("OK")


# noinspection PyUnusedLocal
def get_release(request):
    """
    Return the raven release

    :param request: RequestContext object
    :return: HttpResponse
    """

    release = raven.fetch_git_sha(os.path.dirname(os.path.dirname(__file__)))
    return HttpResponse(json.dumps({"release": release[:7]}))


# Rest API
router = routers.DefaultRouter()
router.register(r'user_list', UserListViewSet)
router.register(r'group_list', GroupListViewSet)

router.register(r'group_permissions', GroupPermissionsViewSet)

urlpatterns = [
    url(r'^dockerStatus/', docker_status),
    url(r'^api-token-auth/', ObtainJSONWebToken.as_view()),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-token-refresh/', RefreshJSONWebToken.as_view()),
    url(r'^api-token-expire/', Unauthenticate.as_view()),
    url(r'^screen_shot/', ScreenShotView.as_view()),
    url(r'^release/', get_release),
    url(r'^index/$', home, name='home'),
    url(r'^api/', include(router.urls)),
]
