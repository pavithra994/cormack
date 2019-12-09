#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from .production import *

import logging


logging.disable(logging.CRITICAL)
DATABASES['default']['HOST'] = 'localhost'
VERBOSE_OCOM_TEST_CLASSES = 1
TEST_WEBDRIVER = 'GOOGLE_CHROME'
LOCAL_SERVER = True
TAKE_TEST_SCREENSHOTS = True
TAKE_TEST_HTML = True
DEBUG = True
