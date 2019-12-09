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

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        xero = connectToXero()
        xero_items = xero.items.all()
        codes = ["%s %s" % (item['Code'], item.get('Name', item.get("Description", ""))) for item in xero_items]

        for item in codes:
            print (item)
