#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf.urls import url
from rest_framework import routers

from . import views

from query.resources.query_def import QueryDefViewSet

router = routers.DefaultRouter()


router.register('query_def', QueryDefViewSet)
urlpatterns = [
    url(r'^meta_data/$', views.MetaDataView.as_view()),
    url(r'^models/$', views.ModelView.as_view()),
]

urlpatterns += router.urls;
