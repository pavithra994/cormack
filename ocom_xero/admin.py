#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib import admin

from api.admin import admin as api_admin
from ocom_xero import forms, models


class XeroConnectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', )
    search_fields = ('name', )
    ordering = ('active', 'name',)

    form = forms.XeroConnectionForm


api_admin.site.register(models.XeroConnection, XeroConnectionAdmin)
