"""tests.simple_element.py - Element classes for Page object model in non-Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import app


class Element(app.SimpleBaseItem):
    """Base HTML Element"""

    item_type = 'Element'


class Link(Element):
    """Representing <a> element"""

    def __init__(self, test_object, redirect_to='', page_to=None, **kwargs):
        """Item initialization method

        :param tests.simple_page.SimplePage or tests.simple_container.Container test_object: the source test object
        :param str alias: the descriptive name of the item
        :param str redirect_to: the url to redirect to when link is clicked
        :param tests.simple_page.SimplePage page_to: the page object to redirect to when link is clicked
        """

        super(Link, self).__init__(test_object, **kwargs)

        if redirect_to == '':
            if page_to is not None:
                self._target_url = page_to.url_path
        else:
            self._target_url = redirect_to

    # noinspection PyUnresolvedReferences
    def click(self, message=''):
        """Perform a click operation

        :param str message: the message to display
        """

        self.utils.console("Clicking on {}...".format(self.name) if message == '' else message)
        self.utils.console("Target url: {}".format(self._target_url), tabs=1)

        response = self.parent.source.client.get(self._target_url)
        if isinstance(self.parent, app.SimpleBaseItem):     # object is probably a container
            self.parent.parent.source.response = response
            self.parent.parent.source.current_url = self._target_url
        elif isinstance(self.parent, app.SimpleFoundation):     # object is probably a page
            self.parent.source.response = response
            self.parent.source.current_url = self._target_url
