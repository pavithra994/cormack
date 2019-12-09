#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

#
#
#

from django.db.models import Q
from django.utils import timezone

import datetime as dt
import pytz


def filter_queryset_by_active_status(queryset, parent=''):
    """Takes as input a queryset and returns a queryset with only active items.
    Model used in the queryset should extend ActiveModel or CodeModel in ocom app.

    :param queryset: the queryset to filter
    :param str parent: if not blank, the name of the related model to look for active status
    :return: the filtered queryset
    """

    # we make it immediate
    today = timezone.now().replace(second=0, microsecond=0) + dt.timedelta(minutes=2)

    if parent == '':
        exclude = {
            'active_start_date__isnull': True
        }
        active_start_date_lte = {
            'active_start_date__lte': today
        }
        active_end_date__gte = {
            'active_end_date__gte': today
        }
        active_end_date__isnull = {
            'active_end_date__isnull': True
        }
    else:
        exclude = {
            parent + '__active_start_date__isnull': True
        }
        active_start_date_lte = {
            parent + '__active_start_date__lte': today
        }
        active_end_date__gte = {
            parent + '__active_end_date__gte': today
        }
        active_end_date__isnull = {
            parent + '__active_end_date__isnull': True
        }

    return queryset.exclude(**exclude).filter(
        Q(**active_start_date_lte), (Q(**active_end_date__gte) | Q(**active_end_date__isnull)))


def filter_queryset_by_expiring_status(queryset, parent='', until=30):
    """Takes as input a queryset and returns a queryset with expiring items from now until the given number of days
    Model used in the queryset should extend ActiveModel or CodeModel in ocom app.

    :param queryset: the queryset to filter
    :param str parent: if not blank, the name of the related model to look for active status
    :param int until: the number of days to include from now. Defaults to 30
    :return: the filtered queryset
    """

    # we make it immediate
    today = timezone.now().replace(second=0, microsecond=0) + dt.timedelta(minutes=2)
    upto = today + dt.timedelta(days=until)

    if parent == '':
        exclude = {
            'active_start_date__isnull': True
        }
        active_end_date_lte = {
            'active_end_date__lte': upto
        }
        active_end_date__gte = {
            'active_end_date__gte': today
        }
        active_end_date__isnull = {
            'active_end_date__isnull': True
        }
    else:
        exclude = {
            parent + '__active_start_date__isnull': True
        }
        active_end_date_lte = {
            parent + '__active_end_date__lte': upto
        }
        active_end_date__gte = {
            parent + '__active_end_date__gte': today
        }
        active_end_date__isnull = {
            parent + '__active_end_date__isnull': True
        }

    return queryset.exclude(**exclude).filter(Q(**active_end_date_lte) & Q(**active_end_date__gte))


def filter_queryset_by_inactive_status(queryset):
    today = timezone.now()
    return queryset.filter(Q(active_start_date__lte=today), (Q(active_end_date__lte=today)))


def get_active_status(active_start_date, active_end_date):
    """
    Returns a boolean on whether the item has an active status. In cases where
    active_start_date == null, then we assume that the item is active.
    """

    # There are null active start dates, just return active status
    if active_start_date:
        utc = pytz.UTC
        now = dt.datetime.today().replace(tzinfo=utc)
        start = active_start_date.replace(tzinfo=utc)
        end = None

        if active_end_date is not None:
            end = active_end_date.replace(tzinfo=utc)

        if start <= now:
            if end is None:
                return True
            else:
                if end >= now:
                    return True
                else:
                    return False

        else:
            return True
    else:
        return False
