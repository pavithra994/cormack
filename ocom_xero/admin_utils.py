#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom_xero.utils import connectToXero


def get_supplier_choices():
    xero = connectToXero()

    try:
        # noinspection PyUnresolvedReferences
        supplier_list = xero.contacts.filter(IsSupplier=True)
        result = sorted([(item["ContactID"], item["Name"]) for item in supplier_list], key=lambda it: it[1])
        result += [("", "--Create New Supplier--")]
    except AttributeError:
        return []

    return result


def get_customer_choices():
    xero = connectToXero()

    try:
        # noinspection PyUnresolvedReferences
        supplier_list = xero.contacts.filter(IsCustomer=True)
        result = sorted([(item["ContactID"], item["Name"]) for item in supplier_list], key=lambda it: it[1])
        result += [("", "--Create New Customer--")]
    except AttributeError:
        return []

    return result


def get_contacts_choices():
    xero = connectToXero()

    try:
        # noinspection PyUnresolvedReferences
        supplier_list = xero.contacts.all()
        result = [(item["ContactID"], item["Name"]) for item in supplier_list]
        result += [("", "--Create New--")]
    except AttributeError:
        return []

    return result
