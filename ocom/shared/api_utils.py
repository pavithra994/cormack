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

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist


def update_model(instance, validated_data, fields):
    for field in fields:
        current = getattr(instance, field, None)
        validated = validated_data.get(field, current)
        setattr(instance, field, validated)

    return instance


def update_model_relation(model, field, instance, form_data, do_not_delete=False, app_label='api'):
    if do_not_delete:
        # This is used for updating a model's many to many field.
        # Instead of instance.repair_types.clear() and instance.repair_types.delete()
        for item in getattr(instance, field).all():
            if item.id not in [form_item.get('id') for form_item in form_data]:
                getattr(instance, field).remove(item)

        # Now save
        for form_item in form_data:
            item_id = form_item.pop('id', '0')

            try:
                related_item = apps.get_model(app_label, model).objects.get(pk=item_id)

                for (key, value) in form_item.items():
                    setattr(related_item, key, value)

                related_item.save()
            except ObjectDoesNotExist:
                related_item = apps.get_model('api', model).objects.create(**form_item)

            getattr(instance, field).add(related_item)

    else:
        getattr(instance, field).all().delete()

        for form_item in form_data:
            print(form_item)
            related_item = apps.get_model('api', model).objects.create(**form_item)
            getattr(instance, field).add(related_item)


def update_or_create_model_then_assign_instance(model, field, instance, validated_data, fields):
    try:
        item = apps.get_model('api', model).objects.get(pk=validated_data.get('id'))
    except:
        item = None

    print("field - %s - %s" % (model, field))
    print(item)
    print(instance)

    if item:
        return update_model(item, validated_data, fields)
    else:
        # Since the model has a FOREIGN key to the instance, we should remove it in validated_data
        if validated_data.get(field, None): validated_data.pop(field)

        # Initialize model object
        to_save = apps.get_model('api', model)()

        # set the model's foreign key instance
        setattr(to_save, field, instance)

        # now set the rest of the model's fields
        for item in fields:
            setattr(to_save, item, validated_data.get(item))

        # Let's save it now
        return to_save
