#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from ocom.models import ActiveModel


class QueryDef(ActiveModel):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Name')
    filter = JSONField(name='filter')
    model_name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Model Name') # the name of the Model this Filter is for.

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ('name',)
