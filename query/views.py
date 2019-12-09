#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.apps import apps
from django.views.generic import View
from rest_framework import viewsets
from rest_framework import filters

from ocom.shared.queryset_utils import filter_queryset_by_inactive_status, filter_queryset_by_active_status

from .models import QueryDef

from ocom.shared.filters import OcomStandardFilter, ActiveFilter, FilterFilter

class ModelView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        # TODO Get List from Config if set else use this code
        result = []
        for app in apps.get_app_configs():
            app_models = app.get_models()
            for model in app_models: # type: ModelBase
                code =  app.name + "." + model._meta.model_name
                name = model._meta.verbose_name.__str__()
                result.append ({'code': code, 'name': name})

        return JsonResponse(result, safe=False)

class MetaDataView(View):

    def get(self, request: HttpRequest, *args, **kwargs):
        fullModelName = request.GET.get("modelName") #type: str

        app_name, model_name = fullModelName.split('.')

        model = apps.get_model(app_name, model_name)

        result = {}

        result['name'] = model.__name__
        result['fields'] = self.get_model_fields(model)


        return JsonResponse(result)

    def get_model_fields(self, model):
        model_fields = []

        for field in model._meta.fields:
            model_fields.append(self.generate_field(field))

        return model_fields

    def generate_field(self, field):
        result = {}

        result['name'] = field.name
        result['type'] = field.__class__.__name__.replace("Field", "")
        result['hidden'] = field.hidden
        result['readonly'] = not field.editable
        result['required'] = (field.editable and not field.null and not field.blank)
        result['verbose_name'] = field.verbose_name
        result['help_text'] = field.help_text
        result['max_length'] = field.max_length
        result['empty_strings_allowed'] = field.empty_strings_allowed
        result['blank'] = field.blank

        return result

