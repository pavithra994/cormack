#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from rest_framework import status, response as drf_response
from rest_framework.views import APIView
from rest_framework_jwt import views as jwt_views
from rest_framework_jwt.settings import api_settings

from ocom.serializers import UserSerializer
from ocom.viewsets import User
from .viewsets import OcomUserRoleMixin
from raven.contrib.django.raven_compat.models import client

import base64
import uuid
import re
import boto

class RefreshJSONWebToken(OcomUserRoleMixin, jwt_views.RefreshJSONWebToken):
    """Inherited refresh_jwt_token class with custom POST method for re-adding session/auth based on a valid JWT"""

    def post(self, request, *args, **kwargs):
        result = super(RefreshJSONWebToken, self).post(request, *args, **kwargs)

        if result.status_code == 200:     # probably a successful refresh
            self.set_user(request, result.data['user']['id'], strict=False)

        return result


class ObtainJSONWebToken(OcomUserRoleMixin, jwt_views.ObtainJSONWebToken):
    """Inherited ObtainJSONWebToken class with custom POST method for manually logging in a user from
    JWT into Django session/auth"""

    def post(self, request, *args, **kwargs):
        result = super(ObtainJSONWebToken, self).post(request, *args, **kwargs)

        if result.status_code == 200:     # probably a successful login

            if result.data.get('user', {}).get('is_superuser', False):
                sudo_id = request.data.get('sudo_id', None)
                if not sudo_id is None:
                    user = User.objects.filter(pk=sudo_id).get()

                    if user:
                        print("SUDO: Using user %s" % (sudo_id))

                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                        payload = jwt_payload_handler(user)

                        result.data['user'] = UserSerializer(user).data  # Swap
                        result.data['token'] = jwt_encode_handler(payload)

            self.set_user(request, result.data['user']['id'], strict=False, backend_login=True)

        return result


class Unauthenticate(OcomUserRoleMixin, APIView):

    def post(self, request, *args, **kwargs):
        self.clear_user(request)
        return drf_response.Response(status=status.HTTP_200_OK)


class ScreenShotView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return render(request, 'feedback/screen_shot.html')

    # noinspection PyMethodMayBeStatic
    def post(self, request):
        img_data = request.POST.get("image")
        filename = str(uuid.uuid4()) + ".png"

        # Upload image to S3 - Make public and get URL
        s3_connection = boto.connect_s3(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        bucket = s3_connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        # noinspection PyUnresolvedReferences
        key = boto.s3.key.Key(bucket, 'screen_shots/' + filename)
        key.set_contents_from_string(base64.b64decode(img_data), replace=True)
        key.make_public()
        image_url = key.generate_url(expires_in=0, query_auth=False)

        details = request.POST.get("details", "")

        original_url = request.POST.get("url", "")
        client.context.clear()  # remove breadcrumbs here we don't need them.
        client.capture('raven.events.Message',
                       stack=False,
                       message='From User: [%s]' % details,
                       data={
                            'culprit': original_url,
                            'request': {
                                'url': original_url,
                                'data': {"screen_shot": image_url},
                                'method': 'POST',
                            },
                       },
                       extra={'url': original_url, 'screen_shot': image_url},
                       tags={'sentry:user': request.POST.get("username"),
                             'screen_shot': image_url,
                             'url': original_url})

        return render(request, 'feedback/done_screen_shot.html')


def add_to_header(response, key, value):
    if response.has_header(key):
        values = re.split(r'\s*,\s*', response[key])

        if value not in values:
            response[key] = ', '.join(values + [value])
    else:
        response[key] = value


def home(request, extra_context=None):
    context = {
        'title': getattr(settings, 'APP_NAME', 'App'),
        'redirect_url': '/static/dev_index.html' if getattr(settings, 'DEV_MODE', False) else '/static/index.html'
    }
    if extra_context:
        context.update(extra_context)

    response = render(request, 'index.html', context)
    add_to_header(response, 'Cache-Control', 'no-cache')
    add_to_header(response, 'Cache-Control', 'max-age=0')
    add_to_header(response, 'Expires', '0')
    add_to_header(response, 'Expires', 'Tue, 01 Jan 1980 1:00:00 GMT')
    add_to_header(response, 'Pragma', 'no-cache')
    return response
