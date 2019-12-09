#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from .base import *
# from custom_storages import MediaStorage

ALLOWED_HOSTS=["*"]

DEV_MODE = True

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = 'jms@cormackgroup.com.au'
EMAIL_HOST_PASSWORD = 'Zuw64831'
EMAIL_PORT = 587

VERBOSE_OCOM_TEST_CLASSES = 1