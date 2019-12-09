# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0084_auto_20190204_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='repaircost',
            name='invoiced',
            field=models.BooleanField(default=False, verbose_name='Invoiced'),
        ),
    ]
