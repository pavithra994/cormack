"""tests.mocks.py - HTTP Mocks Test app

Use this when you need to mock external (3rd party) web pages to interact with your own test pages
"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from selenium.common.exceptions import NoSuchElementException


class HttpMocks(object):
    """Http Mocks class"""

    mock_files = {
        'http://www.facebook.com/somelink': {
            'url': '/facebook_somelink/',
            'file': 'mocks/facebook_somelink.html',
        },
        'https://www.pinterest.com/somelink': {
            'url': '/pinterest_somelink/',
            'file': 'mocks/pinterest_somelink.html',
        },
        'https://instagram.com/somelink': {
            'url': '/instagram_somelink/',
            'file': 'mocks/instagram_somelink.html',
        },
        'https://twitter.com/somelink': {
            'url': '/twitter_somelink/',
            'file': 'mocks/twitter_somelink.html',
        },
    }

    def switch_urls(self, test_page, css_selector, child_css_selector=None):
        """Switch from urls to file

        :param page.SeleniumPage test_page: the test page to base changes to
        :param str css_selector: the css_selector to pattern the search to
        :param str or None child_css_selector: if not None, use as a child css selector while css_selector is main
        """

        elements = test_page.source.browser.find_elements_by_css_selector(css_selector)

        for index, _ in enumerate(elements):
            if child_css_selector is None:
                selector = "{}:nth-of-type({})".format(css_selector, index + 1)
            else:
                selector = "{}:nth-of-type({}) {}".format(css_selector, index + 1, child_css_selector)

            try:
                element = test_page.source.browser.find_element_by_css_selector(selector)
            except NoSuchElementException:
                continue

            href = element.get_attribute('href').lower()

            if href in self.mock_files:
                the_script = 'document.querySelector(\'{}\').href = "{}";'.format(selector,
                                                                                  self.mock_files[href]['url'])
                test_page.source.browser.execute_script(the_script)
                the_script = 'document.querySelector(\'{}\').setAttribute(\'data-url\', "{}");'.format(selector, href)
                test_page.source.browser.execute_script(the_script)
