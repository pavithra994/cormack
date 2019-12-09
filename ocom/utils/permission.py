#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from builtins import dict

from django.contrib.auth.models import User

from ocom.models import GroupPermissions


def calculatePermissionMap (obj: User) -> dict:
    result = {}

    for group in obj.groups.all():
        permissions = GroupPermissions.objects.filter(group=group)

        for perm in permissions:
            for state in perm.states.all():
                if state.deny:
                    result[state.state_name] = {'deny': True}
                else:
                    stateParam = result.setdefault(state.state_name, {'deny': False, 'models': {}})
                    for model in state.models.all():
                        models = stateParam.setdefault("models", {})
                        modelPerm = models.setdefault (model.model_name, {'fields': {}})
                        for field in model.fields.all():
                            fieldParam = modelPerm.get("fields").setdefault(field.field_name,
                                                                            {})

                            if field.deny_read or field.deny_update: # Ignore if it allows BOTH
                                if field.deny_read:
                                    fieldParam['read'] = False # Deny Reading the field

                                if field.deny_update:
                                    fieldParam['update'] = False # Deny Updating the field
                            else:
                                # If there is a field BUT none are denied then it assumes the intention is to explicitly allow
                                fieldParam['update'] = True  # Allow Updating the field
                                fieldParam['read'] = True  # Allow Reading the field
    return result
