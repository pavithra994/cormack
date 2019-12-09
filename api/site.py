#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.contrib.admin import site
from django.contrib.admin.sites import AdminSite


def modify_app_list(context, show='all'):
    """Modify app_list at source

    :param dict context: the context data to get the 'app_list' from
    :param str show: if value is 'all', show all api menus, otherwise, filter bet. 'cdoes', 'modules', and 'auth'
    :return: the modified context data
    """

    # restructure app_list
    new_app_list = []

    for index, item in enumerate(context['app_list']):
        if item['app_label'] == 'api':
            code_item = item.copy()
            api_item = item.copy()
            auth_item = item.copy()
            code_item['name'] = "Code Tables"
            code_item['class'] = "code_tables"
            code_item['app_url'] += '?show=codes'
            code_item['models'] = []
            api_item['models'] = []
            api_item['app_url'] += '?show=modules'
            api_item['name'] = "Modules"
            api_item['class'] = "modules"
            auth_item['app_url'] += '?show=auth'
            auth_item['models'] = []
            auth_item['name'] = "Authentication"
            auth_item['class'] = "authentication"

            for subindex, subitem in enumerate(item['models']):
                if subitem['object_name'].startswith('Code'):
                    code_item['models'].append(subitem)
                elif subitem['object_name'] == 'Role':
                    auth_item['models'].append(subitem)
                else:
                    api_item['models'].append(subitem)

            show_check = show.lower()

            if show_check in ['all', 'codes']:
                new_app_list.append(code_item)

            if show_check in ['all', 'modules']:
                new_app_list.append(api_item)

            if show_check in ['all', 'auth']:
                new_app_list.append(auth_item)
        else:
            if item['app_label'] not in settings.HIDE_ADMIN_MODULES:
                new_app_list.append(item)

    context['app_list'] = new_app_list
    return context


class CormackAdminSite(AdminSite):
    api_path = '/admin/api/'

    def __init__(self, *args, **kwargs):
        super(CormackAdminSite, self).__init__(*args, **kwargs)
        # noinspection PyProtectedMember
        self._registry.update(site._registry)

    def each_context(self, request):
        context = super(CormackAdminSite, self).each_context(request)

        if request.path_info.startswith(self.api_path):
            short_path = request.path_info.replace(self.api_path, '')

            if short_path.startswith('code'):
                context['admin_show_menu'] = 'codes'
            elif short_path.startswith('role'):
                context['admin_show_menu'] = 'auth'
            else:
                context['admin_show_menu'] = 'modules'
        else:
            context['admin_show_menu'] = 'all'

        return context

    def index(self, request, extra_context=None):
        response = super(CormackAdminSite, self).index(request, extra_context)
        response.context_data = modify_app_list(response.context_data)
        return response

    def app_index(self, request, app_label, extra_context=None):
        response = super(CormackAdminSite, self).app_index(request, app_label, extra_context)

        if request.path_info == self.api_path:
            # show modules only
            show_type = request.GET.get('show', 'all')
            response.context_data = modify_app_list(response.context_data, show=show_type)
        else:
            response.context_data = modify_app_list(response.context_data)

        return response
