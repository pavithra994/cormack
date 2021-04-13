#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import json

from django.core.serializers.json import DjangoJSONEncoder
########################################################################
#NEW CODE

from django.core.cache import caches
from xero import Xero
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes

from ocom_xero import models


def connectToXero() -> Xero:
#NEW CODE
    try:
        print("connectToXero")
        cred_state = caches['default'].get('xero_creds')
        print("connectToXero - cred_state")
        credentials = OAuth2Credentials(**cred_state)
        print("connectToXero - credentials")
        if credentials.expired():
            credentials.refresh()
            caches['default'].set('xero_creds', credentials.state)
        print("connectToXero - xero")
        xero = Xero(credentials)
       
    except AttributeError:
        xero = None
    
    return xero
########################################################################
def XeroCleanJSON(jsonData):
    return json.loads(json.dumps(jsonData, cls=DjangoJSONEncoder))

