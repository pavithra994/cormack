#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf.urls import url
from rest_framework import routers

from ocom_xero.views import ListContacts, ListItems, XeroEntityViewSet

router = routers.DefaultRouter()
router.register('xero_entity', XeroEntityViewSet)

urlpatterns = router.urls

urlpatterns +=[
    url(r'^contacts$', ListContacts.as_view(), name='xero_contact'),
    url(r'^items$', ListItems.as_view(), name='xero_contact'),
]
