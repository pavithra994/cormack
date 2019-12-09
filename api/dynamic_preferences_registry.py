#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from dynamic_preferences.types import BooleanPreference, StringPreference, IntegerPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry


@global_preferences_registry.register
class XeroAllowCreateInDebug(BooleanPreference):
    name = 'xero_allow_create_in_debug'
    verbose_name = "Allow Create When in Debug Mode"
    help_text = "When ticked and app is running in Debug it WILL send PUT/POST's to Xero"
    default = False


xero_invoices = Section('XeroInvoices', verbose_name="Xero Invoices")


@global_preferences_registry.register
class XeroInvoiceSaleAcountCode(StringPreference):
    section = xero_invoices
    name = 'sale_account_code'
    verbose_name = "Invoice: Sales Account Code"
    help_text = "The Sales Account code"
    default = '200'


@global_preferences_registry.register
class XeroInvoiceDueDays(IntegerPreference):
    section = xero_invoices
    name = 'due_days'
    help_text = "Number of days to add for Due Date of Invoices"
    verbose_name = "Invoice: Number of Days to Add for Due Date"
    default = 14


@global_preferences_registry.register
class XeroInvoiceBrandingTheme(StringPreference):
    section = xero_invoices
    name = 'branding_theme_id'
    verbose_name = "Invoice: Branding Theme ID"
    help_text = "The Branding Theme ID to use"
    default = '8bb0659e-8095-4c05-8f4d-b4f0bdfa925e'


@global_preferences_registry.register
class XeroInvoiceEmailCustomer(BooleanPreference):
    section = xero_invoices
    name = 'email_customer'
    verbose_name = "Invoice: Email Invoice to Customers"
    help_text = "Should we send emails to the customers that want it."
    default = False


@global_preferences_registry.register
class XeroInvoiceStatus(StringPreference):
    section = xero_invoices
    name = 'status'
    verbose_name = "Invoice: Status"
    default = "AUTHORISED"
    help_text = "Set to 'AUTHORISED' when production or 'DRAFT' when checking manually"


"""
    Xero Purchase Order Settings
"""
xero_purchase_orders = Section('XeroPurchaseOrders', verbose_name="Xero Purchase Orders")


@global_preferences_registry.register
class XeroPOBrandingTheme(StringPreference):
    section = xero_purchase_orders
    name = 'branding_theme_id'
    verbose_name = "Purchase Order: Branding Theme ID"
    help_text = "The Branding Theme ID to use"
    default = '8bb0659e-8095-4c05-8f4d-b4f0bdfa925e'


@global_preferences_registry.register
class XeroInvoiceEmailSubbie(BooleanPreference):
    section = xero_purchase_orders
    name = 'email_subbie'
    verbose_name = "Purchase Order: Send PO to Subbie"
    help_text = "Should we send the PO to the Subbie?"
    default = False


@global_preferences_registry.register
class XeroPOAccountCode(StringPreference):
    section = xero_purchase_orders
    name = 'AccountCode'
    verbose_name = "Purchase Order: Account Code"
    help_text = "The SubContractors account code"
    default = "295"


@global_preferences_registry.register
class XeroPOStatus(StringPreference):
    section = xero_purchase_orders
    name = 'status'
    verbose_name = "Purchase Order: Status"
    default = "AUTHORISED"
    help_text = "Set to 'AUTHORISED' when production or 'DRAFT' when checking manually"


rejected_email_notification = Section('RejectedEmailNotification', verbose_name="Rejected Email Notification")


@global_preferences_registry.register
class EmailNotificationRepairReject(StringPreference):
    section = rejected_email_notification
    name = 'repair_reject_email'
    verbose_name = "Email Notification: Reject Repair"
    default = "admin@cormackgroup.com.au"
    help_text = "Set to a valid email address"


@global_preferences_registry.register
class EmailNotificationJobReject(StringPreference):
    section = rejected_email_notification
    name = 'job_reject_email'
    verbose_name = "Email Notification: Reject Job / Task"
    default = "admin@cormackgroup.com.au"
    help_text = "Set to a valid email address"


@global_preferences_registry.register
class EmailNotificationSource(StringPreference):
    section = rejected_email_notification
    name = 'email_sender'
    verbose_name = "Email Notification Sender"
    default = "jms@cormackgroup.com.au"
    help_text = "Set to a valid email address"


@global_preferences_registry.register
class EmailNotificationDefaultSubbie(IntegerPreference):
    section = rejected_email_notification
    name = 'default_subbie_id'
    verbose_name = "Default Subbie ID"
    default = 9
    help_text = "The Default Subbie ID to set after Task / Repair is rejected " \
                "(make sure ID is present in the Subbie Table)"


job_email_notification = Section('JobEmailNotification', verbose_name="Job Email Notification")


@global_preferences_registry.register
class JobEmailNotificationDefaultRecipient(StringPreference):
    section = job_email_notification
    name = 'default_recipient'
    verbose_name = "Default Recipient Email"
    default = "jms@cormackgroup.com.au" # all Emails MUST Come from here in production otherwise they don't send.
    help_text = "The Default Recipient email to send job notification emails to"

@global_preferences_registry.register
class JobEmailNotificationDefaultRecipient(StringPreference):
    section = job_email_notification
    name = 'default_sender'
    verbose_name = "Default Sender Email"
    default = "noreply@cormackgroup.com.au"
    help_text = "The Default Sender email to send job notification emails to"


@global_preferences_registry.register
class JobEmailNotificationDefaultRecipient(StringPreference):
    section = job_email_notification
    name = 'debug_recipient'
    verbose_name = "Debug Recipient Email"
    default = "debug@ocom.com.au"
    help_text = "The Debug Recipient email to send job notification emails to. If NONE then actual is used."

