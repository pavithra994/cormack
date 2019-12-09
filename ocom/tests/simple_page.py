"""tests.simple_page.py - Page object model for Non-Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.core.urlresolvers import resolve
from ocom.tests import app, utils, simple_element as element


class SimplePage(app.SimpleFoundation):
    """Base page class to initialize the page

    Note: For the sake of efficiency and Javascript events, dynamic links and elements should be handled by
    Selenium pages
    """

    data = []
    # the data to POST or GET from

    def __init__(self, test_case, **kwargs):
        """Simple Page initialization method

        :param ocom.tests.app.OcomTestCaseNoFixtures test_case: the testCase object
        :param str alias: the page alias
        :param str url_path: the url path of the page
        """

        self.source = test_case
        # the testCase object""
        self.utils = test_case.utils
        # The Test Page utilities instance

        try:
            self.alias = kwargs['alias']
        except KeyError:
            if getattr(self, 'alias', None) is None:
                self.alias = ''

        try:
            self.url_path = kwargs['url_path']
        except KeyError:
            if getattr(self, 'url_path', None) is None:
                self.url_path = ''

        self.status_code = ''
        self.content = ''
        self.redirect_to = self.url_path
        # the final redirection path
        self.form_setup()

    @property
    def resolved_name(self):
        """The resolved name based on path"""

        return resolve(self.url_path)

    def _unexpected_url(self, message="Expecting current url as:"):
        """Display a series of messages re: unexpected URLs

        :param message: the message to display
        """

        self.utils.console(message)
        self.utils.console(self.redirect_to, tabs=1)
        self.utils.console("Got:")
        self.utils.console(self.source.current_url, tabs=1)

    def _update_references(self):
        """Update content and status code"""

        self.content = self.source.response.content
        self.status_code = self.source.response.status_code

    # noinspection PyMethodMayBeStatic
    def form_setup(self):
        """Additional steps to run (override on derived classes)"""

        raise NotImplemented("Extend this method by adding elements")

    def save_html(self, filename_without_path, message='', check_path=True, prettify=True):
        """Save html dump of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: The base filename without the absolute path
        :param str message: The message to display
        :param bool check_path: if True, check path with url property
        :param bool prettify: if True, prettifies html
        """

        if check_path and self.url_path not in self.source.current_url:
            self._unexpected_url()
        else:
            message = "Saving html of {}: {}".format(self.alias, filename_without_path) if message == '' else message
            utils.save_html(filename_without_path, self.content, message, prettify=prettify)

    def navigate(self, message=''):
        """Navigate to page's url path

        :param str message: the message to display
        """

        self.utils.console("Changing url to {} ({})...".format(self.redirect_to, self.name)
                           if message == '' else message)
        self.source.response = self.source.client.get(self.redirect_to)
        self.source.current_url = self.redirect_to
        self._update_references()

    def redirect(self, absorb_url=False):
        """Redirect/move to page url

        :param bool absorb_url: if True, the page's url will be set from the redirect url
        """

        if absorb_url:
            self.redirect_to = self.source.current_url

        if self.source.current_url.endswith(self.redirect_to):
            self.utils.console("Confirming redirect to {}: ({})".format(self.name, self.redirect_to))
            self._update_references()
        else:
            self._unexpected_url()


class StandardPage(SimplePage):
    """Standard Page with navigation bar and footer"""

    def form_setup(self):
        """Standard Page elements here"""

        # self.top_nav_menu = container.TopNavbar(self)
        self.logo = element.Link(self, redirect_to='/admin/', alias='Some Logo')


class HomePage(StandardPage):
    """Home Page with carousel, featured finds, and stuff"""

    alias = 'Home Page'
    url_path = '/'


class DashboardPage(StandardPage):
    """Dashboard Page / Admin"""

    alias = 'Admin Dashboard Page'
    url_path = '/admin/'

    def login(self, username, password='admin', redirect_to=None):
        """Attempt to login to admin dashboard with the given credentials

        :param str username: the account name
        :param str password: the account password
        :param str or None redirect_to: the link to redirect to (i.e. ?next=foo)
        :return: the login response
        :rtype: django.http.HttpResponse
        """

        self.utils.console("Signing in as {}...".format(username))
        data = {
            'username': username,
            'password': password
        }
        follow = redirect_to is not None

        if follow:
            data.update({'next': redirect_to})
            self.utils.console("Redirecting to {}...".format(redirect_to), tabs=1)

        self.source.response = self.source.client.post('/admin/login/', data=data, follow=follow)
        self.source.current_url = self.redirect_to
        self._update_references()

    def logout(self):
        """Attempt to logout current account"""

        self.utils.console("Signing out...")
        self.source.response = self.source.client.get('/admin/logout/')
        self.source.current_url = self.redirect_to
        self._update_references()


class SigninPage(StandardPage):
    """Login Page"""

    alias = 'Login Page'
    url_path = '/admin/login/'


class SignoutPage(StandardPage):
    """Logout Page"""

    alias = 'Logout Page'
    url_path = '/admin/logout/'
