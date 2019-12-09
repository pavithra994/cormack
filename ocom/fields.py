"""From https://gist.github.com/danni/f55c4ce19598b2b345ef"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple


class ArraySelectMultiple(SelectMultiple):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def value_omitted_from_data(self, data, files, name):
        return False


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
            'coerce': self.base_field.to_python,
            'widget': ArraySelectMultiple
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)
