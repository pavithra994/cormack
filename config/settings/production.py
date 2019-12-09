#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from .base import *
# from custom_storages import MediaStorage


ALLOWED_HOSTS = ['*', 'cormack.ocom.com.au']

# Change secret key if you want it different in production
# SECRET_KEY = ''

# disable DRF browsable API
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
})

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = 'jms@cormackgroup.com.au'
EMAIL_HOST_PASSWORD = 'Zuw64831'
EMAIL_PORT = 587

VERBOSE_OCOM_TEST_CLASSES = 0
# Set DEBUG as False only when static files are being served thru a web server (apache / nginx)
DEBUG = False