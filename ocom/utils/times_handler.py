#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import datetime

import dateutil
import pytz
from dateutil.tz import gettz
from django.conf import settings

aest = pytz.timezone("Australia/Melbourne")


def parseLocalDateToUTC(localDateStr):
    # timeOffset = aest.utcoffset(datetime.datetime.utcnow())
    # shift_start = localDateStr[:10] + " 00:00:00 +" + str(timeOffset)[:5]  # get the date as Melbourne TimeZone Midnight.
    return dateutil.parser.parse(localDateStr).replace(hour=0, minute=0, second=0, microsecond=0)


def convert(datetime_obj, TYPE=None):
    print("TIME SETTINGS: {}".format(settings.USE_LOCAL_TIMES[TYPE]))

    if TYPE and settings.USE_LOCAL_TIMES[TYPE]:
        # take obj as Local Australia/Melbourne Time and convert to UTC
        print("AEST INPUT IS: {}".format(datetime_obj))
        out = aest.localize(datetime_obj)
        print("CONVERTED TO UTC IN SERVER IS: {}".format(out))
        return out
    else:
        return datetime_obj
