#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.core.management.base import BaseCommand, CommandError

from ocom_xero.models import XeroEntity
from ocom_xero.utils import connectToXero, XeroCleanJSON


def downloadItem (itemName, idName, textName):
    xero = connectToXero()

    manager = getattr(xero, itemName)

    for item in manager.all():
        entity = XeroEntity()
        entity.xero_type = itemName
        entity.xero_id = item.get(idName)
        entity.xero_text = item.get(textName)
        entity.xero_data = XeroCleanJSON(item)
        entity.save()

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        downloadItem("contacts", "ContactID", "Name")
        downloadItem("items", "ItemID", "Name")
        downloadItem("taxrates", "TaxType", "Name")
        downloadItem("accounts", "AccountID", "Name")
