#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

from ocom.viewsets import OcomUserRoleMixin, OcomModelViewSet
from ocom_xero.models import XeroEntity
from ocom_xero.serializer import XeroEntitySerializer
from ocom_xero.utils import connectToXero
from django.core.cache import cache

from query.filter.query_filter import QueryFilter


class ListContacts(APIView):
    """
    View to list all Contacts in Xero as JSON (a Proxy)

    """
    # authentication_classes = (,) #TODO Add back in
    # permission_classes = (,) #TODO Add back in

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        xero = connectToXero()

        #TODO Cache this
        return Response(xero.contacts.all())

class ListItems(APIView):
    """
    View to list all Items in Xero as JSON (a Proxy)

    """

    # authentication_classes = (,) #TODO Add back in
    # permission_classes = (,) #TODO Add back in

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        xero_items = cache.get("xero_items")

        if request.query_params.get("force", "false") == "true":
            xero_items = None

        if xero_items is None:
            xero = connectToXero()

            xero_items = xero.items.all()

            for item in xero_items:
                item['codeName'] = "%s %s" % (item['Code'], item.get('Name', item.get("Description", "")))

            cache.set("xero_items", xero_items, 60) # cache for 1 minute

        return Response(xero_items)

class XeroEntityViewSet(OcomUserRoleMixin, viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.ListModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.UpdateModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = XeroEntity.objects.all()
    serializer_class = XeroEntitySerializer
    filter_backends = (DjangoFilterBackend, QueryFilter)
