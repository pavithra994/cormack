#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import json

from django.core.serializers.json import DjangoJSONEncoder
from xero import Xero
from xero.auth import PrivateCredentials

from ocom_xero import models


def connectToXero() -> Xero:
    connection_info = models.XeroConnection.objects.filter(active=True).first()
    try:
        credentials = PrivateCredentials(connection_info.consumer_key, connection_info.rsa_key)
        xero = Xero(credentials)
    except AttributeError:
        xero = None

    return xero


def XeroCleanJSON(jsonData):
    return json.loads(json.dumps(jsonData, cls=DjangoJSONEncoder))

