"""ocom.tests.asserts.py - Assertions class"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests.utils import console
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def acknowledge_when_done(add_message=None):
    """Add OK message when assertion passes

    :param str or None add_message: additional message to show
    """

    console("OK ({})".format(add_message) if add_message else "OK", tabs=1)


class TestAssertions(object):
    """Test Assertions Class for Ocom Test Cases"""

    @staticmethod
    def assert_true(condition, message="Asserting that condition is True..."):
        """Assert that condition is True

        :param object condition: the value to check if it is true
        :param str message: the message to display
        """

        console(message)

        try:
            assert condition is True
        except AssertionError:
            raise AssertionError("Value is False!")
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_false(condition, message="Asserting that condition is False..."):
        """Assert that condition is False

        :param object condition: the value to check if it is true
        :param str message: the message to display
        """

        console(message)

        try:
            assert condition is False
        except AssertionError:
            raise AssertionError("Value is True!")
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_equal(condition1, condition2, message=''):
        """Assert that condition and value are the same

        :param object condition1: the value to compare condition2 with
        :param object condition2: the value to compare condition1 with
        :param str message: the message to display
        """

        string_value = condition2 if isinstance(condition2, str) else str(condition2)
        console("Asserting that objects are equal to '{}'...".format(string_value) if message == '' else message)

        try:
            assert condition1 == condition2
        except AssertionError:
            raise AssertionError("Values not equal; Left Value: {}; Right Value: {}".format(condition1, string_value))
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_not_equal(condition, value, message=''):
        """Assert that condition and value are not the same

        :param object condition: the condition to compare value with
        :param object value: the value to compare condition with
        :param str message: the message to display
        """

        string_value = value if isinstance(value, str) else str(value)
        console("Asserting that '{}' is NOT equal to '{}'...".format(condition, string_value)
                if message == '' else message)

        try:
            assert condition != value
        except AssertionError:
            raise AssertionError("Values are equal; Left Value: {}; Right Value: {}".format(condition, string_value))
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_contains(haystack, needle, message=''):
        """Assert that needle object is found in the haystack object

        :param object haystack: the object to find needle from
        :param object needle: the value to find in haystack
        :param str message: the message to display
        """

        string_haystack = haystack if isinstance(haystack, str) else str(haystack)
        string_needle = needle if isinstance(needle, str) else str(needle)
        console("Asserting that '{}' contains '{}'...".format(string_haystack, string_needle)
                if message == '' else message)

        try:
            assert string_needle in string_haystack
        except AssertionError:
            raise AssertionError("'{}' is not in '{}'!".format(string_needle, string_haystack))
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_not_contains(haystack, needle, message=''):
        """Assert that needle object is NOT found in the haystack object

        :param object haystack: the object to find needle from
        :param object needle: the value to find in haystack
        :param str message: the message to display
        """

        string_haystack = haystack if isinstance(haystack, str) else str(haystack)
        string_needle = needle if isinstance(needle, str) else str(needle)
        console("Asserting that '{}' does NOT contain '{}'...".format(string_haystack, string_needle)
                if message == '' else message)

        try:
            assert string_needle not in string_haystack
        except AssertionError:
            raise AssertionError("{} is in {}!".format(string_needle, string_haystack))
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_redirect(response, redirect_url, message=''):
        """Assert that response will redirect to specified url

        :param TemplateResponse response: response object to compare redirect_url with
        :param str redirect_url: the redirect url to check for final redirection
        :param str message: the message to display
        """

        console("Asserting that redirect link is {}...".format(redirect_url) if message == '' else message)

        try:
            assert redirect_url in response.redirect_chain[-1][0]
        except AssertionError:
            raise AssertionError("Redirect url {} not in response redirect {}!".format(redirect_url,
                                                                                       response.redirect_chain[-1][0]))
        else:
            acknowledge_when_done()

    def assert_link_response_status_checklist(self, test_case, checklist):
        """Assert that checklist response status entries are correct

        :param TestCase test_case: the test case to run client.get with
        :param list checklist: the response checklist
        format [{'link': 'foo', 'status_code': 123, 'message': 'bar'},...]
        """

        for entry in checklist:
            response = test_case.client.get(entry['link'])
            self.assert_equal(response.status_code, entry['status_code'], entry['message'])


class LiveServerTestAssertions(TestAssertions):
    """Assertions class for Ocom Live Server tests"""

    # noinspection PyUnusedLocal
    def __init__(self, browser=None, **kwargs):
        """LiveServerTestAssertions initialize method

        :param selenium.webdriver.remote.webdriver.WebDriver browser: the browser to use
        """

        self.browser = browser
        """:param selenium.webdriver.remote.webdriver.WebDriver browser: the browser to use"""
        self.page_alias = 'current page'

    def update(self, page=None, test_case=None, alerts_only=False):
        """Update the browser reference for assertions

        This is particularly useful when doing tests with browsers that are being closed on every test case teardown

        :param ocom.tests.page.SeleniumPage page: the current page reference
        :param ocom.tests.app.OcomLiveServerTestCaseNoFixtures test_case: the testCase object
        :param bool alerts_only: if True, update alerts only
        """

        # noinspection PyAttributeOutsideInit
        self.alerts = getattr(page, 'alerts', [])
        """:param list[tests.container.Alert] alerts: list of message alerts"""

        if not alerts_only:
            if test_case is not None:
                self.browser = test_case.browser

            if page is not None:
                self.page_alias = page.name

    def assert_text_in_html(self, text, message=''):
        """Assert the presence of text in the current page's html

        :param list[str] or str text: the text to find
        :param str message: the assertion message to display
        """

        console(message)

        if isinstance(text, str):
            text = [text]

        for sub in text:
            if message == '':
                console("Asserting that '{}' is in {}'s html source...".format(sub, self.page_alias))

            try:
                assert sub in self.browser.page_source
            except AssertionError:
                raise AssertionError("{} not found in {}'s html source!".format(sub, self.page_alias))
            else:
                acknowledge_when_done()

    def assert_text_not_in_html(self, text, message=""):
        """Assert the absence of text in the current page's html

        :param str or list[str] text: the text to find
        :param str message: the assertion message to display
        """

        console(message)

        if isinstance(text, str):
            text = [text]

        for sub in text:
            if message == '':
                console("Asserting that '{}' is NOT in {}'s html source...".format(sub, self.page_alias))

            try:
                assert sub not in self.browser.page_source
            except AssertionError:
                raise AssertionError("'{}' was found in {}'s html!".format(sub, self.page_alias))
            else:
                acknowledge_when_done("Text not found")

    @staticmethod
    def assert_element_value(element, value, message=''):
        """Assert that  element reference value is the same from arg

        :param ocom.tests.element.Element element: element object instance to check for presence
        :param object value: the value to check
        :param str message: the assertion message to display
        """

        console("Asserting that {}'s value is {}...".format(element.name, value) if message == '' else message)
        element.verify_presence(waiting=False, tabs=1)

        try:
            assert element.value == value
        except AssertionError:
            raise AssertionError("Value of {}: '{}'; Compared to '{}'".format(element.alias, element.value, value))
        else:
            acknowledge_when_done()

    def assert_element_present(self, elements, message=''):
        """Assert the presence of element(s) in the page

        :param list[ocom.tests.element.Element] elements: element object(s) to check for presence
        :param str message: the assertion message to display
        """

        console(message)
        the_elements = elements if isinstance(elements, list) else [elements, ]

        for element in the_elements:
            if message == '':
                console("Asserting that '{}' is present in {}...".format(element.alias, self.page_alias))

            try:
                element.verify_presence(waiting=False, tabs=1)
            except NoSuchElementException:
                raise AssertionError("{} is not present in {}!".format(element.alias, self.page_alias))
            else:
                acknowledge_when_done()

    def assert_element_visible(self, elements, message=''):
        """Assert the visibility of element(s) in the page

        :param list[ocom.tests.element.Element] elements: element object(s) to check for visibility
        :param str message: the assertion message to display
        """

        console(message)
        the_elements = elements if isinstance(elements, list) else [elements, ]

        for element in the_elements:
            if message == '':
                console("Asserting that '{}' is visible in {}...".format(element.alias, self.page_alias))

            try:
                element.verify_presence(waiting=False, tabs=1)
            except NoSuchElementException:
                raise AssertionError("{} is not present in {}!".format(element.alias, self.page_alias))

            try:
                assert element.is_visible
            except AssertionError:
                raise AssertionError("{} is not visible!".format(element.alias))
            else:
                acknowledge_when_done()

    def assert_element_not_visible(self, elements, message=''):
        """Assert the hidden status of element(s) in the page

        :param list[ocom.tests.element.Element] elements: element object(s) to check for visibility
        :param str message: the assertion message to display
        """

        console(message)
        the_elements = elements if isinstance(elements, list) else [elements, ]

        for element in the_elements:
            if message == '':
                console("Asserting that '{}' is NOT visible in {}...".format(element.alias, self.page_alias))

            try:
                element.verify_presence(waiting=False, tabs=1)
            except NoSuchElementException:
                raise AssertionError("{} is not present in {}!".format(element.alias, self.page_alias))

            try:
                assert not element.is_visible
            except AssertionError:
                raise AssertionError("{} is visible in {}!".format(element.alias, self.page_alias))
            else:
                acknowledge_when_done("Not visible")

    def assert_element_not_present(self, elements, message=''):
        """Assert the absence of element(s) in the page

        :param list[ocom.tests.element.Element] elements: element object(s) to check for presence
        :param str message: the assertion message to display
        """

        console(message)
        the_elements = elements if isinstance(elements, list) else [elements, ]

        for element in the_elements:
            if message == '':
                console("Asserting that '{}' is NOT present in {}...".format(element.alias, self.page_alias))

            try:
                element.verify_presence(waiting=False, tabs=1)
            except (NoSuchElementException, StaleElementReferenceException):
                console("Element {} does not exist.".format(element.alias), tabs=1)
                acknowledge_when_done()
            else:
                raise AssertionError("Element {} exists!".format(element.alias))

    @staticmethod
    def assert_text_in_element(text, element, message=''):
        """Assert the presence of text in the element's content

        :param str text: the text to find
        :param tests.element.Element element: element object instance to check for text
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is in {}'s content...".format(text, element.name) if message == "" else message)
        content = element.content

        try:
            assert text in content
        except AssertionError:
            raise AssertionError("'{}' was not found in {}'s content: {}!".format(text, element.alias, content))
        else:
            acknowledge_when_done()

    def _assert_alerts(self, use_parent=True, presence=True):
        """Internal assert method for determining presence or absence of alerts

        :param bool use_parent: if True, look for alerts attached to the #messages div element
        :param bool presence: if True, assert for presence; otherwise, assert for absence
        """

        css_selector = '#messages .alert' if use_parent else '.alert'

        try:
            self.browser.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            if presence:
                raise AssertionError("No message alerts found!")

    def assert_no_alerts_in_page(self, message=''):
        """Assert the absence of any alert message in the page's form

        :param str message: the assertion message to display
        """

        console("Asserting that no message is present in {}...".format(self.page_alias) if message == "" else message)
        # look for both alerts
        self._assert_alerts(presence=False)
        self._assert_alerts(use_parent=False, presence=False)

        if len(self.alerts) > 0:
            raise AssertionError("Message alerts contain one or more values.")
        else:
            acknowledge_when_done()

    def _assert_message_check_page(self, message='', alert_type='', use_parent=True):
        """Internal function for assert messages in page

        :param str message: the custom message to display. if value is blank, use generic custom message with
        alert_type
        :param str alert_type: the alert type to mention in message
        :param bool use_parent: if True, use the #messages div as parent for CSS selector checks
        """

        console("Asserting that {} message is present in {}...".format(
            alert_type, self.page_alias) if message == '' else message)

        if use_parent:
            self._assert_alerts()
            count = 0

            for alert in self.alerts:
                if alert.message_type == alert_type:
                    count += 1
                    text = alert.text.encode('ascii', 'ignore').decode('ascii')
                    console("Message: " + text.replace('\n', '\n\t\t\t'), tabs=2)

            if count == 0:
                raise AssertionError("No {} messages found.".format(alert_type))
        else:
            alerts = self.browser.find_elements_by_css_selector('.alert.alert-' + alert_type)
            assert len(alerts) > 0

            for alert in alerts:
                console("Message: " + alert.text, tabs=2)

        acknowledge_when_done()

    def assert_css_selector_is_present(self, css_selector, message=""):
        """Assert the presence of a CSS selector element in the page

        :param str css_selector: the CSS selector to find
        :param str message: the assertion message to display
        """

        console("Asserting that CSS selector {} is present in {}...".format(css_selector, self.page_alias)
                if message == '' else message)
        contents = self.browser.find_elements_by_css_selector(css_selector)

        try:
            assert len(contents) > 0
        except AssertionError:
            raise AssertionError("No elements with CSS selector {} found in {}!".format(css_selector, self.page_alias))
        else:
            acknowledge_when_done()

        # go through each message
        for content in contents:
            if content.text != '':
                console("Content: " + content.text, tabs=1)

    def assert_css_selector_is_not_present(self, css_selector, message=""):
        """Assert the absence of a CSS selector element in the page

        :param str css_selector: the CSS selector to find
        :param str message: the assertion message to display
        """

        console("Asserting that CSS selector {} is NOT present in {}...".format(
            css_selector, self.page_alias) if message == '' else message)

        try:
            self.browser.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            acknowledge_when_done("Element not found")
        else:
            raise AssertionError("Element with CSS selector {} was found!".format(css_selector))

    def assert_css_selector_is_not_visible(self, css_selector, message=""):
        """Assert that the CSS selector element in the page is hidden

        :param str css_selector: the CSS selector to find
        :param str message: the assertion message to display
        """

        console("Asserting that CSS selector {} is not visible in {}...".format(
            css_selector, self.page_alias) if message == '' else message)
        element = self.browser.find_element_by_css_selector(css_selector)

        try:
            assert not element.is_displayed()
        except:
            raise AssertionError("Element with CSS selector {} is visible in {}!".format(css_selector, self.page_alias))
        else:
            acknowledge_when_done("CSS not visible")

    def assert_error_message_in_page(self, message='', use_parent=True, alt=False):
        """Assert the presence of an error message in the form

        :param str message: the assertion message to display
        :param bool use_parent: if True, use the #messages div as parent for CSS selector checks
        :param bool alt: if True, use 'error' instead of 'danger' as alert_type
        """

        self._assert_message_check_page(message, 'error' if alt else 'danger', use_parent)

    def assert_success_message_in_page(self, message='', use_parent=True):
        """Assert the presence of a success message in the page

        :param str message: the assertion message to display
        :param bool use_parent: if True, use the #messages div as parent for CSS selector checks
        """

        self._assert_message_check_page(message, 'success', use_parent)

    def assert_warning_message_in_page(self, message='', use_parent=True):
        """Assert the presence of a warning message in the page

        :param str message: the assertion message to display
        :param bool use_parent: if True, use the #messages div as parent for CSS selector checks
        """

        self._assert_message_check_page(message, 'warning', use_parent)

    def assert_info_message_in_page(self, message='', use_parent=True):
        """Assert the presence of an info message in the page

        :param str message: the assertion message to display
        :param bool use_parent: if True, use the #messages div as parent for CSS selector checks
        """

        self._assert_message_check_page(message, 'info', use_parent)

    def assert_text_in_title(self, text, message=''):
        """Assert that text is in page title

        :param str text: the text to look for
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is in {}'s title...".format(text, self.page_alias) if message == '' else message)

        try:
            assert text in self.browser.title
        except:
            raise AssertionError("{} was not found in {} title: {}!", text, self.page_alias, self.browser.title)
        else:
            acknowledge_when_done()

    def assert_text_not_in_title(self, text, message=''):
        """Assert that text is not in page title

        :param str text: the text to look for
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is NOT in {}'s title...".format(text, self.page_alias)
                if message == '' else message)

        try:
            assert text not in self.browser.title
        except:
            raise AssertionError("{} was found in {} title: {}!".format(text, self.page_alias, self.browser.title))
        else:
            acknowledge_when_done()

    def assert_page_in_url(self, page, message=''):
        """Assert that page url path is in current url

        :param SeleniumPage page: the page to look for
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is in {}'s url...".format(page.url_path, self.page_alias)
                if message == '' else message)

        try:
            assert self.browser.current_url.endswith(page.url_path)
        except:
            raise AssertionError("Browser url: {}; {}'s url: {}".format(self.browser.current_url, self.page_alias,
                                                                        page.url_path))
        else:
            acknowledge_when_done()

    def assert_text_in_url(self, text, message=''):
        """Assert that text is in current url

        :param str text: the text to look for
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is in {}'s url...".format(text, self.page_alias) if message == '' else message)

        try:
            assert text in self.browser.current_url
        except:
            raise AssertionError("{} was not found in browser url: {}!".format(text, self.browser.current_url))
        else:
            acknowledge_when_done()

    def assert_text_not_in_url(self, text, message=''):
        """Assert that text is not in current url

        :param str text: the text to look for
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is NOT in {}'s url...".format(text, self.page_alias) if message == '' else message)

        try:
            assert text not in self.browser.current_url
        except:
            raise AssertionError("{} was found in browser url: {}!".format(text, self.browser.current_url))
        else:
            acknowledge_when_done()

    # noinspection PyUnresolvedReferences
    def assert_text_in_mail(self, text, email, message=''):
        """Assert that text is in e-mail

        :param list[str] or str text: the text or list of text to look for
        :param dict email: the email message (django.core.mail)
        :param str message: the assertion message to display
        """

        console(message)

        if isinstance(text, str):
            text = [text]

        for sub in text:
            if message == '':
                console("Asserting that '{}' is in {} mail message...".format(sub, self.page_alias))

            try:
                assert sub in email.body
            except AssertionError:
                raise AssertionError("'{}' was not found in the email!".format(sub))

        acknowledge_when_done()

    @staticmethod
    def assert_recipient_in_mail(recipient, email, message=''):
        """Assert that e-mail address is a recipient

        :param str recipient: the recipient email address to look for
        :param dict email: the email message (django.core.mail)
        :param str message: the assertion message to display
        """

        console("Asserting that '{}' is a recipient in mail...".format(recipient) if message == '' else message)

        try:
            # noinspection PyUnresolvedReferences
            assert recipient in email.to
        except AssertionError:
            raise AssertionError("{} is not an e-mail recipient!".format(recipient))
        else:
            acknowledge_when_done()

    @staticmethod
    def assert_empty_outbox(outbox, message=''):
        """Assert that e-mail outbox is empty

        :param list outbox: the e-mail outbox (django.core.mail)
        :param str message: the assertion message to display
        """

        console("Asserting that mail outbox is empty (no e-mail sent)..." if message == '' else message)

        try:
            assert len(outbox) == 0
        except AssertionError:
            raise AssertionError("Outbox contains mail!")
        else:
            acknowledge_when_done()
