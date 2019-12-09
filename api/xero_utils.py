#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from itertools import groupby
from typing import List

from django.conf import settings
import datetime
import json

from datetime import timedelta

from django.conf import Settings
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder


from api.models import Job, Client, Subbie, Repair
from ocom_xero.models import XeroEntity
from ocom_xero.utils import connectToXero
from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()

def checkCanCreate():
    """
        If Debug Mode and this preference not set then don't allow creating
        Move of a failsafe to stop it creating accidently.
    """

    if settings.DEBUG:
        return global_preferences['xero_allow_create_in_debug']
    else:
        return True



def createContactForClient(client:Client) -> Client:
    contact = {
        "ContactStatus": "ACTIVE",
        "Name": client.name,
        "IsCustomer": True, # IsCustomer and IsSupplier is ignored but atleast we show intention
        "IsSupplier": False,
        "DefaultCurrency": "AUD"
    }

    if checkCanCreate():
        xero = connectToXero()

        newContact = xero.contacts.put(contact)

        print (newContact)

        client.xero_customer = newContact[0].get("ContactID")
        client.save()

        return client
    else:
        return None

def createContactForSubbie (subbie: Subbie) -> Subbie:
    contact = {
        "ContactStatus": "ACTIVE",
        "Name": subbie.name,
        "IsCustomer": False, # IsCustomer and IsSupplier is ignored but atleast we show intention
        "IsSupplier": True,
        "DefaultCurrency": "AUD"
    }

    if checkCanCreate():
        xero = connectToXero()

        newContact = xero.contacts.put(contact)

        print(newContact)

        subbie.xero_supplier = newContact[0].get("ContactID")
        subbie.save()

        return subbie
    else:
        return None

def createJobPurchaseOrder (job:Job) -> XeroEntity:

    if not job.sub_contractor.xero_supplier:
        subbie = createContactForSubbie (job.sub_contractor)
    else:
        subbie = job.sub_contractor

    today = datetime.date.today()

    lineItems = [{
             'AccountCode': global_preferences['XeroPurchaseOrders__AccountCode'], # SubContractors account
             'Description': job.description,
             'TaxType': 'INPUT',
             'Quantity': job.sqm,
             'UnitAmount': subbie.rate_per_m,
             }]

    reference = job.address + "\n" + job.suburb

    purchaseOrder = {
         'Telephone': '61 5261 8397',
         'CurrencyCode': 'AUD',
         'AttentionTo': 'Luke Cormack ',
         'LineAmountTypes': 'Exclusive',
         'Date': today,
         'DeliveryInstructions': job.description,
         'DeliveryDate': job.pour_date,

         'LineItems': lineItems,

         'Status' : global_preferences['XeroInvoices__status'], # "AUTHORISED"
         'IsDiscounted': False,
         'HasAttachments': False,
         'DeliveryAddress': '9 Boneyards Ave\nTorquay\nVIC\n3228\nAustralia',
         'CurrencyRate': 1.0,
         'Reference': reference,
         'Contact': {"ContactID": subbie.xero_supplier}
    }

    if global_preferences["XeroPurchaseOrders__branding_theme_id"] != "NONE":
        purchaseOrder['BrandingThemeID'] =  global_preferences["XeroPurchaseOrders__branding_theme_id"]

    if checkCanCreate():
        xero = connectToXero()

        result = xero.purchaseorders.put(purchaseOrder)

        print (result)

        xeroPurchaseOrder = XeroEntity()

        xeroPurchaseOrder.other_id = job.id
        xeroPurchaseOrder.other_name = "job"
        xeroPurchaseOrder.xero_type = "PurchaseOrder"
        xeroPurchaseOrder.xero_id = result[0].get("PurchaseOrderID")
        xeroPurchaseOrder.xero_code = result[0].get("PurchaseOrderNumber")
        xeroPurchaseOrder.xero_text = result[0].get("Reference")
        xeroPurchaseOrder.total = result[0].get("Total")
        xeroPurchaseOrder.xero_data = json.loads(json.dumps(result[0], cls=DjangoJSONEncoder)) # Clean Convert Date/Times etc to Strings

        xeroPurchaseOrder.save()

        job.xero_purchase_order = xeroPurchaseOrder
        job.save()

        return xeroPurchaseOrder
    else:
        return None

def createRepairPurchaseOrder (repair:Repair) -> XeroEntity:

    if not repair.repair_subbie.xero_supplier:
        subbie = createContactForSubbie (repair.repair_subbie)
    else:
        subbie = repair.repair_subbie

    today = datetime.date.today()

    lineItems = [{
             'AccountCode': global_preferences['XeroPurchaseOrders__AccountCode'], # SubContractors account
             'Description': repair.job.description,
             'TaxType': 'INPUT',
             'Quantity': 0, # ??
             'UnitAmount': subbie.rate_per_m,
             }]

    reference = repair.job.address + "\n" + repair.job.suburb

    purchaseOrder = {
         'Telephone': '61 5261 8397',
         'CurrencyCode': 'AUD',
         'AttentionTo': 'Luke Cormack ',
         'LineAmountTypes': 'Exclusive',
         'Date': today,
         'DeliveryInstructions': repair.comments,
         'DeliveryDate': today,

         'LineItems': lineItems,

         'Status' : global_preferences['XeroInvoices__status'], # "AUTHORISED"
         'IsDiscounted': False,
         'HasAttachments': False,
         'DeliveryAddress': '9 Boneyards Ave\nTorquay\nVIC\n3228\nAustralia',
         'CurrencyRate': 1.0,
         'Reference': reference,
         'Contact': {"ContactID": subbie.xero_supplier}
    }

    if global_preferences["XeroPurchaseOrders__branding_theme_id"] != "NONE":
        purchaseOrder['BrandingThemeID'] =  global_preferences["XeroPurchaseOrders__branding_theme_id"]

    if checkCanCreate():
        xero = connectToXero()

        result = xero.purchaseorders.put(purchaseOrder)

        print (result)

        xeroPurchaseOrder = XeroEntity()

        xeroPurchaseOrder.other_id = repair.id
        xeroPurchaseOrder.other_name = "repair"
        xeroPurchaseOrder.xero_type = "PurchaseOrder"
        xeroPurchaseOrder.xero_id = result[0].get("PurchaseOrderID")
        xeroPurchaseOrder.xero_code = result[0].get("PurchaseOrderNumber")
        xeroPurchaseOrder.xero_text = result[0].get("Reference")
        xeroPurchaseOrder.total = result[0].get("Total")
        xeroPurchaseOrder.xero_data = json.loads(json.dumps(result[0], cls=DjangoJSONEncoder)) # Clean Convert Date/Times etc to Strings

        xeroPurchaseOrder.save()

        repair.xero_purchase_order = xeroPurchaseOrder
        repair.save()

        return xeroPurchaseOrder
    else:
        return None

def createJobInvoice(job:Job) -> List[XeroEntity]:
    """
    Create an Invoice from a Job in Xero.

    :param job: The Job To create the invoice for.
    :return: The XeroInvoice entity we created
    """

    if not job.client.xero_customer:
        client = createContactForClient (job.client)
    else:
        client = job.client

    uninvoiced_cost_list = [job_cost for job_cost in job.job_costs.all() if not job_cost.invoiced]

    result = []

    job_cost_to_save= []

    for po_number, cost_list in groupby(uninvoiced_cost_list , key=lambda k: k.purchase_order_number):
        lineItems = []
        for job_cost in cost_list:
                lineItems.append({
                    "ItemCode": job_cost.xero_item_code,
                    "Description": job_cost.details,
                    "Quantity":job_cost.quantity,
                    "UnitAmount":job_cost.unit_price,
                    "TaxType": "OUTPUT",
                    "AccountCode": global_preferences['XeroInvoices__sale_account_code']
                })

                job_cost.invoiced = True
                job_cost_to_save.append(job_cost)

        today = datetime.date.today()
        due = today + timedelta(days=global_preferences['XeroInvoices__due_days']) # TODO Change to configurable value..

        invoice_ref = po_number + " " + job.address + " " + job.suburb #TODO No State + Postcode??

        invoice = {"Type":"ACCREC",
                   "CurrencyCode": "AUD",
                   "Contact":{"ContactID":client.xero_customer},
                   "Date": today,
                   "DueDate": due,
                   "LineAmountTypes":"Exclusive",
                   'Reference': invoice_ref,
                   "LineItems":lineItems,
                   "CurrencyRate": 1.0,
                   "Status": global_preferences['XeroInvoices__status'], #  "AUTHORISED"
                   "SentToContact": False, #  we Sent it TODO: Change to True when we send it.
                   "IsDiscounted": False,
                   "CISDeduction": 0.0, # Assume we don't use this in AU
        }

        if global_preferences["XeroInvoices__branding_theme_id"] != "NONE":
            invoice['BrandingThemeID'] =  global_preferences["XeroInvoices__branding_theme_id"]

        if checkCanCreate():
            xero = connectToXero()

            result = xero.invoices.put(invoice)

            print (result)

            xeroInvoice = XeroEntity()

            xeroInvoice.other_id = job.id
            xeroInvoice.other_name = "job"
            xeroInvoice.xero_type = "Invoice"
            xeroInvoice.xero_text = result[0].get("Reference")
            xeroInvoice.xero_id = result[0].get("InvoiceID")
            xeroInvoice.xero_code = result[0].get("InvoiceNumber")
            xeroInvoice.total = result[0].get("Total")
            xeroInvoice.xero_data = json.loads(json.dumps(result[0], cls=DjangoJSONEncoder)) # Clean Convert Date/Times etc to Strings

            xeroInvoice.save()

            # Success now save it.
            for job_cost in job_cost_to_save:
                job_cost.save()

            result.append(xeroInvoice)
        else:
            result.append(None)

    return result



def createRepairInvoice(repair:Repair) -> XeroEntity:
    """
    Create an Invoice from a Job in Xero.

    :param job: The Job To create the invoice for.
    :return: The XeroInvoice entity we created
    """

    job = repair.job

    if not job.client.xero_customer:
        client = createContactForClient (job.client)
    else:
        client = job.client

    lineItems = []
    repair_cost_to_save = []

    for repair_cost in repair.repair_costs.all():
        if not repair_cost.invoiced:
            lineItems.append({
                "ItemCode": repair_cost.xero_item_code,
                "Description": repair_cost.details,
                "Quantity":repair_cost.quantity,
                "UnitAmount":repair_cost.unit_price,
                "TaxType": "OUTPUT",
                "AccountCode": global_preferences['XeroInvoices__sale_account_code']
            })

            repair_cost.invoiced = True
            repair_cost_to_save.append(repair_cost)

    today = datetime.date.today()
    due = today + timedelta(days=global_preferences['XeroInvoices__due_days']) # TODO Change to configurable value..

    purchaseOrderNumbers =  repair.po_number # IS THIS THE SAME LOGIC?? ", ".join([po.number for po in job.purchase_orders.all()])

    invoice_ref = purchaseOrderNumbers + " " + job.address + " " + job.suburb #TODO No State + Postcode??

    invoice = {"Type":"ACCREC",
               "CurrencyCode": "AUD",
               "Contact":{"ContactID":client.xero_customer},
               "Date": today,
               "DueDate": due,
               "LineAmountTypes":"Exclusive",
               'Reference': invoice_ref,
               "LineItems":lineItems,
               "CurrencyRate": 1.0,
               "Status": global_preferences['XeroInvoices__status'], #  "AUTHORISED"
               "SentToContact": False, #  we Sent it TODO: Change to True when we send it.
               "IsDiscounted": False,
               "CISDeduction": 0.0, # Assume we don't use this in AU
    }

    if global_preferences["XeroInvoices__branding_theme_id"] != "NONE":
        invoice['BrandingThemeID'] =  global_preferences["XeroInvoices__branding_theme_id"]

    if checkCanCreate():
        xero = connectToXero()

        result = xero.invoices.put(invoice)

        print (result)

        xeroInvoice = XeroEntity()

        xeroInvoice.other_id = repair.id
        xeroInvoice.other_name = "repair"
        xeroInvoice.xero_type = "Invoice"
        xeroInvoice.xero_text = result[0].get("Reference")
        xeroInvoice.xero_id = result[0].get("InvoiceID")
        xeroInvoice.xero_code = result[0].get("InvoiceNumber")
        xeroInvoice.total = result[0].get("Total")
        xeroInvoice.xero_data = json.loads(json.dumps(result[0], cls=DjangoJSONEncoder)) # Clean Convert Date/Times etc to Strings

        xeroInvoice.save()

        for repair_cost in repair_cost_to_save:
            repair_cost.save()

        return xeroInvoice
    else:
        return None
