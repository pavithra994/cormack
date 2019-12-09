#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.postgres.fields import JSONField
from django.db import models

from ocom.models import OcomModel

DISALLOW_EMPTY_CONFIG = {
    'blank': False,
    'null': False,
}

MONEY_CONFIG = {
    'max_digits': 12,
    'decimal_places': 2,
    'default': 0,
}

class XeroConnection(models.Model):
    name = models.CharField(verbose_name="Name", null=False, max_length=50)
    rsa_key = models.CharField(verbose_name="RSA Key", null=False, max_length=1000)
    consumer_key = models.CharField(verbose_name="Consumer Key", null=False, max_length=1000)
    active = models.BooleanField(verbose_name="Active", default=True)

    class Meta:
        db_table = 'xero_connection'
        verbose_name = "Xero Connection"
        verbose_name_plural = "Xero Connections"

class XeroEntity(models.Model):
    xero_id = models.CharField(verbose_name="Xero ID", null=True, max_length=50, db_index=True)  # ie The Xero ID
    xero_type = models.CharField(verbose_name="Xero Type", null=True, max_length=50, db_index=True)  # ie "Customer" or "Item"
    xero_data = JSONField(verbose_name="Xero Data", null=False)
    xero_text = models.CharField(verbose_name="Description", null=True, max_length=255, db_index=True)  # ie The Customer's Name or item.Name etc.
    xero_code = models.CharField(verbose_name="Code", null=True, max_length=255,
                                 db_index=True)  # ie The Item.Code, Invoice.Invoice_Number, PurchaseOrder.PurchaseOrderNumber

    # For "Relationship" to other Entities
    other_id = models.IntegerField(verbose_name="Other ID", null=True, blank=True, db_index=True)  # ie the job ID
    other_name = models.CharField(verbose_name="Other Name", null=True, blank=True, max_length=50, db_index=True)  # ie "job" or "repair"

    total = models.DecimalField(verbose_name="Total Amount", **MONEY_CONFIG, **DISALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'xero_entity'
        verbose_name = "Xero Entity"
        verbose_name_plural = "Xero Entities"
