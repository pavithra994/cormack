# -*- coding: utf-8 -*-

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

from __future__ import unicode_literals
from django.db import migrations, models
import django


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    if django.VERSION >= (1, 10):
        dependencies = [
            ('auth', '0008_alter_user_username_max_length'),
        ]

    operations = [
        migrations.CreateModel(
            name='GroupPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(db_index=False, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='group_permissions_group', to='auth.Group', verbose_name='Group')),
            ],
            options={
                'verbose_name': 'Group Permission',
                'verbose_name_plural': 'Group Permission',
                'db_table': 'group_permissions',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='GroupState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_name', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='State Name')),
                ('deny', models.BooleanField(default=False, verbose_name='Deny')),
            ],
            options={
                'verbose_name': 'Group State',
                'verbose_name_plural': 'Group State',
                'db_table': 'group_state',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='GroupStateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_uri', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Base URI')),
                ('model_name', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Model Name')),
            ],
            options={
                'verbose_name': 'Group State Model',
                'verbose_name_plural': 'Group State Models',
                'db_table': 'group_state_model',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='GroupStateModelField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Field Name')),
                ('can_read', models.BooleanField(default=True, verbose_name='Can Read')),
                ('can_update', models.BooleanField(default=True, verbose_name='Can Update')),
            ],
            options={
                'verbose_name': 'Group State Model Field',
                'verbose_name_plural': 'Group State Model Fields',
                'db_table': 'role_state_model_field',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='groupstatemodel',
            name='fields',
            field=models.ManyToManyField(blank=True, default=None, to='ocom.GroupStateModelField', verbose_name='Fields'),
        ),
        migrations.AddField(
            model_name='groupstate',
            name='models',
            field=models.ManyToManyField(blank=True, default=None, to='ocom.GroupStateModel', verbose_name='Models'),
        ),
        migrations.AddField(
            model_name='grouppermissions',
            name='states',
            field=models.ManyToManyField(blank=True, default=None, to='ocom.GroupState', verbose_name='States'),
        ),
    ]
