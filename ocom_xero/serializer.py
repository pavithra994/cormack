#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from rest_framework import serializers
from rest_framework.fields import JSONField

from ocom_xero.models import XeroEntity


class XeroEntitySerializer(serializers.ModelSerializer):
    xero_data = JSONField(True)

    class Meta:
        model = XeroEntity
        fields = ('id', 'xero_id', 'xero_type', 'xero_data', 'xero_text', 'xero_code', 'other_id', 'other_name', 'total')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }
