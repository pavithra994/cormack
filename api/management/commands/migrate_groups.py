#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from api.models import Role


class Command(BaseCommand):
    help = 'Migrate Groups'

    def handle(self, *args, **options):
        roles = Role.objects.all()

        group_mapping = [
            {
                'field_name': 'supervisor',
                'group_name': 'Supervisor'
            },
            {
                'field_name': 'administrator',
                'group_name': 'Administrator'
            },
            {
                'field_name': 'subcontractor',
                'group_name': 'Subcontractor'
            },
            {
                'field_name': 'client_manager',
                'group_name': 'ClientManager'
            },
            {
                'field_name': 'employee',
                'group_name': 'Employee'
            }
        ]

        for role in roles:
            role.user.groups.clear() # clear for this user.

            # this is where we do some permission set updates
            for item in group_mapping:
                group, _ = Group.objects.get_or_create(name=item['group_name'])

                if getattr(role, item['field_name'], False):
                    group.user_set.add(role.user)
                else:
                    group.user_set.remove(role.user)
