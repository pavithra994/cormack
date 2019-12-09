#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django import forms

from ocom_xero import models


class XeroConnectionForm(forms.ModelForm):
    rsa_key = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.XeroConnection
        fields = ('name', 'active', 'rsa_key', 'consumer_key')
