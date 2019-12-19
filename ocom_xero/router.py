#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.conf.urls import url
from rest_framework import routers

from ocom_xero.views import ListContacts, ListItems, XeroEntityViewSet
from django.views.generic.base import RedirectView

from urllib.parse import quote as urlencode

# The Xero sign-in URL,built out of stuff from settings.
if True:
    XERO_SIGNIN_URL = "https://login.xero.com/identity/connect/authorize?" + \
        "response_type=code" + "&" + \
        "client_id={}".format(urlencode(settings.XERO_OAUTH2_CLIENT_ID)) + "&" + \
        "redirect_uri={}".format(urlencode(settings.XERO_OAUTH2_REDIRECT_URI)) + "&" + \
        "scope=openid profile email offline_access accounting.transactions" + "&" + \
        "state={}".format(None)
else:
    XERO_SIGNIN_URL = "https://dev-396343.oktapreview.com/oauth2/default/v1/authorize?" + \
        "response_type=code" + \
        "&client_id=0oaoy0k6z4oUMy6T80h7" + \
        "&redirect_uri=" + urlencode("https://www.oauth.com/playground/authorization-code.html") + \
        "&scope=photo+offline_access" + \
        "&state=COXXxXPCVAJWG8E5"
print("\nXERO_SIGNIN_URL")
print(XERO_SIGNIN_URL.replace('%', '%%'))

router = routers.DefaultRouter()
router.register('xero_entity', XeroEntityViewSet)

urlpatterns = router.urls

urlpatterns +=[
    url(r'^contacts$', ListContacts.as_view(), name='xero_contact'),
    url(r'^items$', ListItems.as_view(), name='xero_contact'),
    url(r'^connect-oauth$', RedirectView.as_view(url=XERO_SIGNIN_URL.replace('%', '%%'), permanent=False), name='xero_connect_oauth')
    # The OAuth callback lives in api/router.py for no good reason. - Robert Howe
]