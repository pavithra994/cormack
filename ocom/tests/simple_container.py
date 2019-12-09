"""tests.simple_container.py - Container for Page object model in non-Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import app, simple_element as element


class Container(app.SimpleBaseItem):
    """General container with bound controls"""

    item_type = 'Container'

    def __init__(self, test_object, **kwargs):
        """Container initialization method

        :param tests.simple_page.SimplePage test_object: the source test object
        :param str alias: the descriptive name of the item
        """

        super(Container, self).__init__(test_object, **kwargs)
        self.source = test_object.source
        self.controls_setup()

    # noinspection PyMethodMayBeStatic
    def controls_setup(self):
        """Override this on inheriting classes"""

        raise NotImplemented("Override this function by adding elements")


class TopNavbar(Container):
    """Representing navigational bar group of buttons and search form"""

    alias = 'Top Navigation Bar'

    def controls_setup(self):
        """Top Navigation Bar controls"""
        self.login = element.Link(self, redirect_to='/accounts/signin/', alias='Navbar->Login Link')
        self.logout = element.Link(self, redirect_to='/accounts/signout/', alias='Navbar->Logout Link')
        """
        self.search_query = element.TextBox(self, name='q', alias='Navbar->Search Box')
        self.search_button = element.Button(self, css_selector='form.search button[type=submit]',
                                            alias='Navbar->Search Icon Button')
        """


class LandingPageContent(Container):
    """Representing navigational bar group of buttons and search form"""

    alias = 'Landing Page Content'

    def controls_setup(self):
        """Landing Page Content controls"""

        raise NotImplemented("Override this function by adding elements")
