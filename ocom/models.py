#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

import hashlib
import json


class OcomModel(models.Model):
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ListModel(OcomModel):
    _is_deleted = models.BooleanField(default=False)
    _display_order = models.IntegerField(default=0)

    class Meta:
        abstract = True


class ActiveModel(OcomModel):
    active_start_date = models.DateTimeField(verbose_name="Active Start Date", default=timezone.now)
    active_end_date = models.DateTimeField(verbose_name="Active End Date", blank=True, null=True)

    @property
    def is_active(self):
        """Return True if record is active"""

        if self.active_end_date is None:
            return True

        return timezone.now() < self.active_end_date

    class Meta:
        abstract = True


class CodeModel(ActiveModel):
    code = models.CharField(unique=True, max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=False, null=False, verbose_name='Description/Name')

    def __str__(self):
        return "{}".format(self.description)

    class Meta:
        ordering = ('description',)
        abstract = True


class HashModel(OcomModel):
    """Hash Key model for offsite caching purposes"""

    key = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)

    def update_models(self, model_name):
        all_of_model = self.objects.filter(model_name=model_name)

        for item in all_of_model:
            item.save(force_update=True)

    def is_stale(self, key, difference_in_seconds=86400, delete=True):
        """Return True if key does not exist or key is stale beyond the number of seconds
        :param str key: the hash key to check
        :param int difference_in_seconds: minimum number of seconds to check for condition to be True
        :param bool delete: if True, delete key from hash if stale
        :return: True if stale
        :rtype: bool
        """

        item = self.objects.filter(key=key)
        difference = timezone.now() - item.modified_date

        if item is not None:
            if difference.seconds >= difference_in_seconds:
                if delete:
                    item.delete()

                return True
            else:
                return False

        return True

    @staticmethod
    def get_key_from_json(json_data):
        """Retrieve md5 hash key from JSON data
        :param dict json_data: the json data to get the hash from
        :return: the hash key
        :rtype: str
        """

        return hashlib.md5(json.dumps(json_data, sort_keys=True).encode('utf-8')).hexdigest()

    class Meta:
        abstract = True


def default_active_date():
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)


class GroupPermissions(models.Model):
    class Meta:
        db_table = "group_permissions"
        verbose_name = "Group Permission"
        verbose_name_plural = "Group Permission"
        ordering = ['group__name', ]



    def __unicode__(self):
        return u'%s' % self.id  # TODO

    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name="group_permissions_group",
                              verbose_name="Group", null=False, blank=False, default=None, editable=True, help_text="",
                              unique=False, db_index=False, )
    states = models.ManyToManyField('GroupState', verbose_name="States", blank=True, default=None, editable=True,
                                    help_text="", unique=False, db_index=False, )

    details = models.CharField(verbose_name="Details", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, max_length=500, )

class GroupState(models.Model):
    class Meta:
        db_table = "group_state"
        verbose_name = "Group State"
        verbose_name_plural = "Group State"
        ordering = ['state_name', ]


    def __unicode__(self):
        return u'%s' % self.state_name

    state_name = models.CharField(verbose_name="State Name", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, max_length=255, )
    deny = models.BooleanField(verbose_name="Deny", blank=True, default=False, editable=True, help_text="",
                               unique=False, db_index=False, )
    details = models.CharField(verbose_name="Details", null=True, blank=True, default=None, editable=True,
                               help_text="", unique=False, db_index=False, max_length=500, )

    models = models.ManyToManyField('GroupStateModel', verbose_name="Models", blank=True, default=None,
                                         editable=True, help_text="", unique=False, db_index=False, )


class GroupStateModel(models.Model):
    class Meta:
        db_table = "group_state_model"
        verbose_name = "Group State Model"
        verbose_name_plural = "Group State Models"
        ordering = ['model_name', ]


    def __unicode__(self):
        return u'%s' % self.model_name

    base_uri = models.CharField(verbose_name="Base URI", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, max_length=255, )

    model_name = models.CharField(verbose_name="Model Name", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, max_length=255, )
    fields = models.ManyToManyField('GroupStateModelField', verbose_name="Fields", blank=True, default=None,
                                    editable=True, help_text="", unique=False, db_index=False, )


class GroupStateModelField(models.Model):
    class Meta:
        db_table = "role_state_model_field"
        verbose_name = "Group State Model Field"
        verbose_name_plural = "Group State Model Fields"
        ordering = ['field_name', ]


    def __unicode__(self):
        return u'%s' % self.field_name  # TODO

    field_name = models.CharField(verbose_name="Field Name", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, max_length=255, )
    deny_read = models.BooleanField(verbose_name="Deny Read", blank=True, default=False, editable=True, help_text="",
                                   unique=False, db_index=False, )
    deny_update = models.BooleanField(verbose_name="Deny Update", blank=True, default=False, editable=True, help_text="",
                                     unique=False, db_index=False, )





