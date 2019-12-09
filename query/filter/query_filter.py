#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import datetime
import json

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

#TODO implement NOT
#TODO implement Special cases ie #NextFinancialYear = 1/7/2019 -> 30/6/2020 etc for Dates Between

'''
    Process Querys in JSON ie this is the Active filter we use all the time
    
    {"logic":"and", "criteria":[{"operation":"le","name":"active_start_date","params":[],"special":"date-now"},
            {"or":[{"operation":"is_null","name":"active_end_date"},
                   {"operation":"ge","name":"active_end_date","special":"date-now"}]}]}
'''
class SpecialCodes():

    def date_now(self):
        return [datetime.datetime.today()] #TODO Check is date and time and tZ stuff..

    def date_today(self):
        return [datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)] #TODO Check is date only and tZ stuff..

    def date_tomorrow(self):
        return [datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)] #TODO Check

    def date_yesterday(self):
        return [datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)] #TODO Check

    # TODO Add other codes here..

class QueryFilter(BaseFilterBackend):
    """

    """

    special_codes = SpecialCodes()

    def filter_queryset(self, request, queryset, view):
        queryText = request.query_params.get('query', None)

        if queryText is not None:
            query = json.loads(queryText)

            if (query):
                the_filter = self.executeQuery(query, request)

                return queryset.filter(the_filter) #translate JSON Query into Q objects

        return queryset

    def executeQuery(self, query, request):
        return self.executeItem(query, request)

    def executeItem(self, query, request):
        if 'name' in query:
            return self.executeCriteria (query, request)
        if 'logic' in query:
            if query.get("logic", None) == "and":
                return self.executeAnd (query, request)

            if query.get("logic", None) == "or":
                return self.executeOr(query, request)

    operations = {'eq'          : {'django_op': 'exact', 'param_count': 1},
                  'gt'          : {'django_op': 'gt', 'param_count': 1},
                  'ge'          : {'django_op': 'gte', 'param_count': 1},
                  'lt'          : {'django_op': 'lt', 'param_count': 1},
                  'le'          : {'django_op': 'lte', 'param_count': 1},
                  'is_null'     : {'django_op': 'isnull', 'param_count': 0, 'params': True},
                  'is_not_null' : {'django_op': 'isnull', 'param_count': 0, 'params': False},
                  'between'     : {'django_op': 'range', 'param_count': 2},
                  'contains'    : {'django_op': 'contains', 'param_count': 1},
                  'icontains'   : {'django_op': 'icontains', 'param_count': 1}
                  }

    def executeCriteria(self, query, request):

        op = self.operations[query['operation']]

        if "special" in query:
            codeName = query.get("special").replace("-", "_")

            if codeName:
                func = getattr(self.special_codes, codeName)
                if (func):
                    query['params'] = func()

        params = query.get("params", [])

        if len(params) != op['param_count']:
            raise ValueError("Wrong number of parameters for {0}".format(query['name']))

        for index, aparam in enumerate(params):
            if isinstance(aparam, str) and aparam.startswith("::"):
                params[index] = request.query_params.get(aparam.replace("::", ""))

        if op['param_count'] == 1:
            params = params[0]  # use just ONE value

        if 'params' in op:
            params = op['params'] # Use params from operation if there are parameters ie for isnull


        kwargs = {
            '{0}__{1}'.format(query['name'], op['django_op']): params
        }

        return Q(**kwargs)

    def executeAnd(self, query, request):
        q_objects = Q()  # Create an empty Q object to start with

        for queryItem in query['criteria']:
            q_objects &= self.executeItem(queryItem, request)

        return q_objects

    def executeOr(self,  query, request):
        q_objects = Q()  # Create an empty Q object to start with

        for queryItem in query['criteria']:
            q_objects |= self.executeItem(queryItem, request)

        return q_objects

