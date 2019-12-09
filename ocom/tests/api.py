"""tests.api.py - API Endpoint test module"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from . import simple_page


class ApiEndpoint(simple_page.SimplePage):

    def form_setup(self):
        """do nothing for now"""
        pass

    def _update_references(self):
        """Update content and status code"""

        self.content = self.source.response.data
        self.status_code = self.source.response.status_code

    def post(self, data, message='', token=''):
        """POST data to Api's url path

        :param dict data: the data to send
        :param str message: the message to display
        :param str token: the jwt token to use
        """

        self.utils.console("Posting data to url ({})...".format(self.redirect_to) if message == '' else message)

        if token:
            data.update({"Authorization": "JWT {}".format(token)})

        self.source.response = self.source.client.post(self.redirect_to, data=data)
        self.source.current_url = self.redirect_to
        self._update_references()

    def navigate(self, message='', token=''):
        """Navigate to Api's url path

        :param str message: the message to display
        :param str token: the jwt token to use
        """

        self.utils.console("Changing url to {} ({})...".format(self.redirect_to, self.name)
                           if message == '' else message)

        if token:
            data = {
                "Authorization": "JWT {}".format(token)
            }
        else:
            data = None

        self.source.response = self.source.client.get(self.redirect_to, data=data)
        self.source.current_url = self.redirect_to
        self._update_references()


class AuthTokenApiEndpoint(ApiEndpoint):
    alias = "API Auth Token Endpoint"
    url_path = '/api-token-auth/'
    token = ''

    def authenticate(self, username, password='admin'):
        """Attempt to authenticate and get token

        :param str username: the account name
        :param str password: the account password
        :return: the token response
        :rtype: django.http.HttpResponse
        """

        self.utils.console("Signing in as {}...".format(username))
        data = {
            'username': username,
            'password': password
        }

        self.source.response = self.source.client.post(self.url_path, data=data)
        self._update_references()
        self.token = self.content.get('token')
