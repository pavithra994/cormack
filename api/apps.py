#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from __future__ import unicode_literals
from django.apps import AppConfig

import logging


LOGGER = logging.getLogger('cormack')


class CormackConfig(AppConfig):
    name = 'api'
