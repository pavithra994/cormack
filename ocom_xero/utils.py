#
# utils.py
# Robert Howe <rc@rchowe.com>
#
# Originally written by OCom, re-written due to a change from OAuth 1.0a to OAuth 2.0
#

import json

from django.core.serializers.json import DjangoJSONEncoder
from xero import Xero
from api import models

def connectToXero() -> Xero:
    """
    Connect to Xero using OAuth 2.0.
    """

    credentials = models.XeroOAuth2Information.objects.first()
    if credentials == None:
        return None
    
    try:
        return Xero(credentials)
    except AttributeError:
        return None
    
    return None
    
def XeroCleanJSON(jsonData):
    """
    Clean JSON by stringifying it and reading the string.
    """
    return json.loads(json.dumps(jsonData, cls=DjangoJSONEncoder))
