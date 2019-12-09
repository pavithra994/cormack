#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import login, logout
from rest_framework import status, viewsets, response
from ocom.shared.queryset_utils import filter_queryset_by_inactive_status, filter_queryset_by_active_status


User = apps.get_model('auth', 'User')
# The session id to base user data on
SESSION_USER_ID = 'user_id'


class OcomActiveModelViewMixin(object):
    def destroy(self, request, *args, **kwargs):
        """
        For Active Models disable instead of delete

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # noinspection PyUnresolvedReferences
        obj = self.get_object()
        # obj.active_end_date = dt.datetime.now()
        obj.active_end_date = timezone.now()
        obj.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_active(self, request, queryset):
        ''' Standard "Filter' for FitlerFilter Backend to get Active Items '''
        return filter_queryset_by_active_status(queryset)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_inactive(self, request, queryset):
        ''' Standard "Filter' for FitlerFilter Backend to get InActive Items '''
        return filter_queryset_by_inactive_status(queryset)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_all(self, request, queryset):
        ''' Standard "Filter' for FitlerFilter Backend to get All Items '''
        return queryset


class OcomUserRoleMixin(object):
    """A mixin used for identifying currently logged in user from JWT

    Sample Usage:
        from ocom.views import OcomUserRoleMixin

        class SomeViewSet(OcomModelViewSet, OcomUserRoleMixin):
            def __init__(self, *args, **kwargs):
                user_id = kwargs.pop('user_id')
                super(SomeViewSet, self.)__init__(*args, **kwargs)
                self.set_user(self.request, user_id)

            def get_something(self):
                ...
                user = self.get_user(self.request)   # will return the user
                ...

    """

    @staticmethod
    def set_user(request, user_id, strict=True, backend_login=False):
        """Sets the currently logged in user from JWT to the session variable or the contextRequest user
        :param request: the Context Request object
        :param int user_id: the user ID
        :param bool strict: if True, set the session variable or login if it is different from the current value
        :param bool backend_login: if True, manually performs a login. May only be triggered if
        JWT_LOGIN_REQUEST_CONTEXT_USER settings is False
        """

        user = User.objects.get(pk=user_id)

        if getattr(settings, 'JWT_LOGIN_REQUEST_CONTEXT_USER', False):
            if not hasattr(user, 'backend'):
                user.backend = 'django.contrib.auth.backends.ModelBackend'

            if request.user != user and strict:
                login(request, user)
        else:
            if backend_login:
                if not hasattr(user, 'backend'):
                    user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user)

            if not request.session.session_key:
                request.session.create()

            if request.session.get(SESSION_USER_ID) != user_id and not strict:
                request.session[SESSION_USER_ID] = user_id

    @staticmethod
    def get_user(request):
        """Return the currently logged in user from JWT
        :param request: the Context Request object
        :return the User instance
        :rtype: django.contrib.auth.models.User
        """

        if getattr(settings, 'JWT_LOGIN_REQUEST_CONTEXT_USER', False):
            return request.user
        else:
            user_id = request.session.get(SESSION_USER_ID, None)
            return User.objects.none() if user_id is None else User.objects.get(pk=user_id)

    @staticmethod
    def clear_user(request):
        """Removes a user from session variable or requestContext
        :param request: the Context Request object
        """

        if getattr(settings, 'JWT_LOGIN_REQUEST_CONTEXT_USER', False):
            # We really don't care if the token provided is ok or not, as we just log out the current user.
            logout(request)
        else:
            request.session[SESSION_USER_ID] = None


class OcomModelViewSet(viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.ListModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.UpdateModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """
    ModelViewSets in views.py should extend OcomModelViewSet.
    Deleting data should only set the active_end_date into today.

    Usage:
    from ocom.utils.drf_snippets import filter_queryset
    class CompanyRateModelViewSet(OcomModelViewSet):
        def get_queryset(self):
            queryset = CompanyRate.objects.all()
            queryset = filter_queryset(self.request.query_params, queryset)
            return queryset
    """

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        # obj.active_end_date = dt.datetime.now()
        obj.active_end_date = timezone.now()
        obj.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_active(self, request, queryset):
        return filter_queryset_by_active_status(queryset)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_inactive(self, request, queryset):
        return filter_queryset_by_inactive_status(queryset)

    def get_queryset(self):
        result = super(OcomModelViewSet, self).get_queryset()
        filter_set = self.request.query_params.get('filter')

        if filter_set:
            if not isinstance(filter_set, list):
                filter_set = [filter_set]

            for each_filter in filter_set:
                if each_filter == 'active':
                    result = self.filter_active(self.request, result)

                if each_filter == 'inactive':
                    result = self.filter_inactive(self.request, result)

        return result


class CodeModelViewSet(OcomModelViewSet):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def filter_all(self, request, queryset):
        return queryset


class BulkModelViewSet(OcomModelViewSet):
    """
    Bulk Model Viewsets that rely on id List to populate values

    Note: use bulk_field to determine the field name from request data to get which shall contain the value to set
    """

    bulk_field = 'something'

    # noinspection PyUnusedLocal
    def put(self, request, *args, **kwargs):
        id_list = request.data.get('ids', [])
        field_name = request.data.get('fieldName', '')
        field_to_set = request.data.get(self.bulk_field, '')

        if id_list and field_name:
            try:
                self.queryset.filter(id__in=id_list).update(**{field_name: field_to_set})
            # TODO: get specific exception
            except Exception as e:
                return response.Response({'result': 'ERROR'}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({'result': 'OK'}, status=status.HTTP_200_OK)
