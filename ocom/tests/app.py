"""tests.app.py - This module contains extended test cases and associated classes for Ocom web apps

Current issues:
    1. tests may lock up every time a webdriver is set, usually at the beginning (currently implemented signals to
       disrupt these)
    2. there are still random instances of page loading timeouts happening, although not frequent (at this point,
       re-initializing browser and re-running page is done to rectify such issue)
"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import datetime
import time
import warnings

from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from . import wait, utils, mocks, asserts


BROWSER_MAPPER = {
    utils.GOOGLE_CHROME: utils.chrome_webdriver,
    utils.FIREFOX: utils.firefox_webdriver,
    utils.PHANTOMJS: utils.phantomjs_webdriver,
    utils.NO_BROWSER: utils.no_webdriver,
}

MAX_TRIES = 2


class OcomTestUtils(object):
    """Utilities class for Ocom Tests"""

    @property
    def verbosity(self):
        """Get the verbosity level

        :return: the current verbosity level. Verbosity of 0 prevents messages from being displayed on the console
        :rtype: int
        """

        return 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0

    def _call_command(self, instruction, message=''):
        """Wrapper function to run management.call_command

        :param str or list instruction: the instruction or instruction set to run
        :param str message: the dump message to display
        """

        return utils.call_command_silent(instruction, message=message, verbosity=self.verbosity)

    def console(self, message, tabs=0, newlines=0):
        """Wrapper to console function; Display message to console if verbose setting is greater than 0

        :param str message: the message to show
        :param int tabs: the number of tabs to prepend message
        :param int newlines: the number of newline characters to prepend to the message
        """

        utils.console(message, tabs=tabs, newlines=newlines, verbosity=self.verbosity)

    def start_timer(self, key, timers, message='', tabs=0):
        """Start timer based on key

        :param str key: specific identifier to be used when getting timer values (see timer function)
        :param str message: the message to display
        :param dict timers: the timers store to use
        :param int tabs: the number of tabs to prepend message
        """

        if self.verbosity > 0:
            self.console(message, tabs=tabs)
            timers[key] = datetime.datetime.now()

    def time_elapsed(self, key, timers, tabs=0):
        """Show elapsed time based on key

        :param str key: specific identifier for timer values
        :param dict timers: the timers store to use
        :param int tabs: the number of tabs to prepend messages
        """

        time_elapsed = datetime.datetime.now()

        if key in timers and time_elapsed > timers[key]:
            utils.show_time_difference(timers[key], time_elapsed, verbosity=self.verbosity, tabs=tabs)

    # noinspection PyMethodMayBeStatic
    def load_fixtures(self, sequence=None, clear_db=False, populate_countries=True):
        """Wrapper function to load_fixtures

        :param list sequence: the loading sequence
        :param bool clear_db: if True, clears the test DB prior to loading the fixtures
        :param bool populate_countries: if True, populates country data before loading fixtures
        """

        utils.load_fixtures(sequence, clear_db=clear_db, populate_countries=populate_countries)

    def delay(self, seconds, tabs=0, message="Getting idle:"):
        """Wait for a number of seconds

        :param float seconds: the seconds to wait
        :param int tabs: the tabs to prepend to the wait message
        :param str message: the dump message to display
        """

        if seconds > 0 and message != '':
            self.console("{} {} second{}".format(message, seconds, "" if seconds == 1 else "s"), tabs=tabs)

        time.sleep(seconds)

    def clear_data(self, message="Clearing Test DB contents...", tabs=1):
        """Convenience function to clear test DB data

        :param str message: the message to show
        :param int tabs: the number of tabs to prepend message
        """

        utils.clear_data(message=message, verbosity=self.verbosity, tabs=tabs)

    @staticmethod
    def escape_string(value):
        """Escape/ Strip string value

        :param str value: string to escape
        :return: escaped string
        :rtype: str
        """

        if '"' in value and "'" in value:
            substrings = value.split("\"")
            result = ["concat("]

            for substring in substrings:
                result.append("\"%s\"" % substring)
                result.append(", '\"', ")
            result = result[0:-1]

            if value.endswith('"'):
                result.append(", '\"'")

            return "".join(result) + ")"

        if '"' in value:
            return "'%s'" % value

        return "\"%s\"" % value


class SimpleFoundation(object):
    """Simple Foundation class with a timers store"""

    timers = dict()
    """:param dict timers: The timers dict used by set_start_time and time_elapsed functions"""

    @property
    def name(self):
        """Attempt to get name of item

        :return: the extracted name
        :rtype: str
        """

        alias = getattr(self, 'alias', '')

        if alias != '':
            return alias

        resolved_name = getattr(self, 'resolved_name', '')

        if resolved_name != '':
            return resolved_name

        return str(self)


class Foundation(SimpleFoundation):
    """Foundation class for Selenium Tests"""

    @property
    def is_browser_phantomjs(self):
        """Check if browser is PhantomJS

        :return: if browser is PhantomJS, True
        :rtype: bool
        """

        source = getattr(self, 'source', None)
        return False if source is None else source.browser_type == utils.PHANTOMJS

    @property
    def is_browser_firefox(self):
        """Check if browser is Firefox

        :return: if browser is Firefox, True
        :rtype: bool
        """

        source = getattr(self, 'source', None)
        return False if source is None else source.browser_type == utils.FIREFOX

    # noinspection PyMethodMayBeStatic
    def _load_page(self, page_object, url):
        """Change browser page with exception handling

        :param tests.page.SeleniumPage or tests.element.Element page_object: the object to get source, utils, and
        reference page from
        :param str url: the url to go to
        """

        tries = 1
        while tries <= MAX_TRIES:
            try:
                page_object.source.browser.get(url)
            except TimeoutException:
                if tries >= MAX_TRIES:
                    raise TimeoutException("Maximum number of tries attempted for change url to: {}".format(url))
                else:
                    page_object.utils.console("Change url timed out. Trying again...", tabs=1)
                    tries += 1
            else:
                break

    @staticmethod
    def _wait_until_timeout(timeout, message="Waiting..."):
        """Perform wait until timeout expires

        :param float timeout: the timeout to expire
        :param str message: the message to display before commencing wait
        """

        utils.wait_for_timeout(timeout, message)

    @staticmethod
    def _wait_until_ready_state_complete(page_object):
        """Attempt to wait until ready state is set as complete

        :param tests.page.SeleniumPage or tests.element.Element page_object: the object to get source, utils, and
        reference page from
        """

        def page_has_loaded():
            """Check document.readyState

            :return: page_state
            :rtype: bool
            """

            page_state = page_object.source.browser.execute_script('return document.readyState;')
            return page_state == 'complete'

        utils.wait_for_function(page_has_loaded, finish_message="DOM Page ready state is complete.",
                                prewait=page_object.source.browser_type == utils.FIREFOX)

    def _wait_until_page_loaded(self, page_object, timeout=None, check_ready_state=True, check_staleness=True):
        """Perform wait until reference page is stale and the page has loaded

        :param tests.page.SeleniumPage or tests.element.Element page_object: the object to get source, utils, and
        reference page from
        :param float timeout: timeout to expire, in seconds
        :param bool check_ready_state: if True, check for DOM ready state
        :param bool check_staleness: if True, check for staleness of page
        """

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        if check_ready_state:
            self._wait_until_ready_state_complete(page_object)

        if not check_staleness:
            self._wait_until_timeout(timeout)

        if check_staleness and page_object.reference_page is not None:
            tries = 0

            while tries < MAX_TRIES:
                try:
                    WebDriverWait(page_object.source.browser, timeout).until(expected_conditions.staleness_of(
                        page_object.reference_page))
                except TimeoutException:
                    tries += 1

                    if tries >= MAX_TRIES:
                        raise TimeoutException(
                            "Selenium command timed out while attempting to check staleness of reference page...")
                    else:
                        page_object.utils.console(
                            "Timed out while attempting to check staleness of reference page. Trying again...", tabs=1)
                else:
                    break

        """
        try:
            # TODO: don't forget to add ocom id in html!
            page_object.source.browser.find_element_by_id('ocom')
        except NoSuchElementException:
            page_object.utils.console("Non-Ocom page detected...", tabs=1)
        else:
            try:
                # TODO: we probably do not need this
                page_object.source.browser.find_element_by_id('oops')
            except NoSuchElementException:
                pass
            else:
                page_object.utils.console("Error page detected...", tabs=1)
        """

    @staticmethod
    def safe_find_element_by_css_selector(element, css_selector):
        """Run a safe find_element_by_css_selector method

        :param selenium.webdriver.remote.webelement.WebElement element: the element reference to find css with
        :param str css_selector: the CSS selector to find a sub-element with
        :return: the sub-element based on the CSS selector
        :rtype: selenium.webdriver.remote.webelement.WebElement
        """

        try:
            result = element.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            return None

        return result


class SimpleBaseItem(SimpleFoundation):
    """Base item class for extension by elements, containers, and frames in non-Selenium tests"""

    item_type = 'Item'
    """:param str item_type: identification type for use in console messages"""

    # noinspection PyUnusedLocal
    def __init__(self, test_object, alias='', **kwargs):
        """Item initialization method

        :param tests.simple_page.SimplePage or tests.simple_container.Container test_object: the source test object
        :param str alias: the descriptive name of the item
        """

        self.source = self.parent = test_object
        """:param tests.ocom.OcomTestCaseNoFixtures source: The Test Page source"""
        self.utils = test_object.utils
        """:param tests.ocom.OcomTestUtils utils: The Test Page utilities instance"""

        if alias != '':
            self.alias = alias


class BaseItem(Foundation):
    """Base item class for extension by elements, containers, and frames in Selenium tests

    Note: reference updates are enforced except where indicated
    """

    item_type = 'Item'
    """:param str item_type: identification type for use in console messages"""

    def __init__(self, test_object, alias='', **kwargs):
        """Item initialization method

        :param tests.page.SeleniumPage or tests.container.Container test_object: the source test object
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        self.parent = test_object
        self.source = test_object.source
        # The Test Page source
        self.utils = test_object.utils
        # The Test Page utilities instance

        if alias != '':
            self.alias = alias

        try:
            self.css_selector = kwargs['css_selector']
        except KeyError:
            if getattr(self, 'css_selector', None) is None:
                self.css_selector = ''
                """:param str css_selector: the CSS selector of the item"""

        self.use_parent_css_selector = getattr(self.parent, 'element_as_source', False)
        self.angular = kwargs.get('angular', False)
        self._dom_id = kwargs.get('dom_id', '')
        self._locator = kwargs.get('name', '')
        self._class_name = kwargs.get('class_name', '')
        self._xpath = kwargs.get('xpath', '')
        self._description = None
        self._page_url = None
        self.reference_page = None

    @property
    def is_visible(self):
        """Get status of item's visibility on the page

        :return: if visible, True
        :rtype: bool
        """

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.is_displayed()

    @property
    def is_enabled(self):
        """Get status of item if it is enabled or not

        :return: if enabled, True
        :rtype: bool
        """

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.is_enabled()

    @property
    def content(self):
        """Get the item's current content (including those not displayed)"""

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.get_attribute('textContent')

    @property
    def text(self):
        """Get the item's current text"""

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.text

    @property
    def value(self):
        """Get the item's current value"""

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.get_attribute('value')

    @property
    def source_url(self):
        """Get the item's source url"""

        # since this is a property, we force a reference update
        self._update_reference(inform=False)
        return self._reference.get_attribute('src')

    @property
    def href(self):
        """Get the item's href (for links)"""

        # since this is a property, we force a reference update
        self._update_reference(inform=False)
        return self._reference.get_attribute('href')

    @property
    def data_url(self):
        """Get the item's href (for links)"""

        # since this is a property, we force a reference update
        self._update_reference(inform=False)
        return self._reference.get_attribute('data-url')

    def _perform_click(self, message, use_script=False):
        """Do a click operation on the element reference

        Note: Update references should be handled by the method caller

        :param str message: the message to display
        :param bool use_script: if True, use javascript command to issue click; otherwise, use selenium method
        """

        self.utils.console("Clicking on {}...".format(self.name) if message == '' else message)

        if use_script:
            if self.use_parent_css_selector:
                css_selector = self.parent.css_selector \
                    if self.css_selector == '*' and self.use_parent_css_selector \
                    else '{} {}'.format(self.parent.css_selector, self.css_selector)
            else:
                css_selector = self.css_selector

            self.utils.console("via script with CSS selector: {}".format(css_selector), tabs=1)
            self.source.browser.execute_script("document.querySelector('{}').click();".format(css_selector))
        else:
            try:
                self._reference.click()
            except TimeoutException:
                raise TimeoutException("Timeout after clicking on {}!".format(self.name))
            else:
                self.utils.console("Click event went through.", tabs=1)

    def _send_escape_key(self):
        """Send an escape key (ESC) to item's reference object

        Note: calling method is expected to run update_reference prior to this
        """

        self._reference.send_keys(Keys.ESCAPE)

    def _reference_has_css_selector(self, css_selector):
        """Checks if reference has a CSS selector

        Note: calling method is expected to run update_reference prior to this

        :param css_selector: the CSS selector to look for from reference
        :return: if found, True
        :rtype: bool
        """

        try:
            self._reference.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            return False
        else:
            return True

    def _wait_until_css_selector_is_present(self, css_selector, timeout):
        """Perform wait until CSS selector is found on the page

        :param str css_selector: the CSS selector to find
        :param float timeout: timeout to expire, in seconds
        """

        try:
            WebDriverWait(self.source.browser, timeout).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        except TimeoutException:
            raise TimeoutException("Selenium command timed out while looking for CSS selector {}.".format(
                css_selector))

    def _check_presence_of_css_selector(self, css_selector):
        """Check if CSS selector exists from a page

        :param str css_selector: the CSS selector to find
        """

        try:
            self.source.browser.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            raise NoSuchElementException("Unable to find CSS selector {}.".format(css_selector))

    def _get_elements_from_css_selector(self, css_selector):
        """
        Get element references from a CSS selector on a page

        :param str css_selector: the CSS selector to find
        :return: list of WebElement references
        :rtype: list[selenium.webdriver.remote.webelement.WebElement]
        """

        try:
            elements = self.source.browser.find_elements_by_css_selector(css_selector)
            return elements
        except NoSuchElementException:
            raise NoSuchElementException(
                "Unable to find elements with CSS selector {} on the current page".format(css_selector))

    def _is_reference_page_stale(self):
        """Get status of reference page staleness

        :return: if stale, True
        :rtype: bool
        """

        if self.reference_page is not None:
            try:
                # obtained from expected_conditions.staleness_of code
                self.reference_page.is_enabled()
            except StaleElementReferenceException:
                return True

        return False

    # noinspection PyProtectedMember
    def _update_reference(self, timeout=None, waiting=False, force=False, inform=True, strict=True, tabs=0):
        """If reference is not set, look for item in the current page and update description

        :param float timeout: timeout to expire, in seconds
        :param bool waiting: if True, wait until element is detected or until timeout occurs
        :param bool force: if True, forces update of item reference
        :param bool inform: if True and no changes to the reference was done, show confirmation message
        :param bool strict: if True and item is not found, raise an exception
        :param int tabs: the number of tabs to prepend messages
        """

        tabs_plus_one = tabs + 1

        if self._is_reference_page_stale():
            self.reference_page = None
            self.remove_reference()

        if self.reference_page is None:
            self.reference_page = self.source.browser.find_element_by_tag_name('html')

        if self.angular and hasattr(self, '_reference'):
            try:
                self._reference.is_enabled()
            except StaleElementReferenceException:
                force = True

        if getattr(self, '_reference', None) is None or force:
            self.utils.start_timer('item_find', self.timers)

            if timeout is None:
                timeout = wait.PAGE_TIMEOUT

            if self.use_parent_css_selector:
                self.parent._update_reference(tabs=tabs)
                reference_source = self.parent._reference

                if self.css_selector == '*':
                    self._reference = reference_source
                    self.utils.console("Setting {} {} to parent reference...".format(self.item_type, self.name),
                                       tabs=tabs_plus_one)
            else:
                reference_source = self.source.browser

            if self.css_selector != '*':
                reference_mapper = {
                    '_dom_id':
                        ("ID: {}".format(self._dom_id),
                         reference_source.find_element_by_id,
                         "#" + self._dom_id),
                    '_locator':
                        ("Locator: {}".format(self._locator),
                         reference_source.find_element_by_name,
                         "#id_" + self._locator),
                    '_class_name':
                        ("Class Name: {}".format(self._class_name),
                         reference_source.find_element_by_class_name,
                         "." + self._class_name),
                    'css_selector':
                        ("CSS Selector: {}".format(self.css_selector),
                         reference_source.find_element_by_css_selector,
                         self.css_selector),
                    '_xpath':
                        ("XPath: {}".format(self._xpath),
                         reference_source.find_element_by_xpath,
                         self._xpath),
                }

                find_function = None
                reference = ''
                actual_css_selector = ''

                for attribute in reference_mapper:
                    reference = getattr(self, attribute, '')

                    if reference != '':
                        self._description, find_function, actual_css_selector = reference_mapper[attribute]
                        break

                if actual_css_selector != '' and self.css_selector != actual_css_selector:
                    self.css_selector = actual_css_selector

                if waiting:
                    self._wait_until_css_selector_is_present(self.css_selector, timeout)

                self.utils.console("Looking for {} {}...".format(self.item_type, self.name), tabs=tabs)

                try:
                    self._reference = find_function(reference)
                    # The Selenium WebElement of the item
                except AttributeError:
                    raise AttributeError(
                        "Please provide a reference for your {} (e.g. CSS selector, DOM Id, name, etc.)".format(
                            self.item_type))
                except NoSuchElementException:
                    if strict:
                        raise NoSuchElementException("No element found for {})".format(self.item_type))
                    else:
                        return

                self.utils.console("Found {} {}.".format(self.item_type, self.name), tabs=tabs_plus_one)

                if self.use_parent_css_selector:
                    self.utils.console("Parent {}".format(self.parent._description), tabs=tabs_plus_one)
                    self.utils.console("Child {}".format(self._description), tabs=tabs_plus_one)
                else:
                    self.utils.console(self._description, tabs=tabs_plus_one)

            self.utils.time_elapsed('item_find', self.timers, tabs=tabs_plus_one)
        else:
            try:
                # obtained from expected_conditions.staleness_of code
                self._reference.is_enabled()
            except StaleElementReferenceException:
                if strict:
                    raise StaleElementReferenceException(
                        "Item is stale: {} {} with {}.".format(self.item_type, self.name, self._description))
                else:
                    self._reference = None

            if inform:
                self.utils.console("{} is available.".format(self.name), tabs=tabs_plus_one)

    def remove_reference(self):
        """Remove the current reference to prevent stale element exceptions from happening"""

        if hasattr(self, '_reference'):
            delattr(self, '_reference')

    def verify_presence(self, message='', waiting=True, timeout=None, tabs=0):
        """Wait until item is visible or check if present. No exceptions should be thrown out for this to pass

        :param str message: the message to display before looking for the element
        :param bool waiting: if True, wait until element is detected or until timeout occurs
        :param float timeout: the number of seconds to expire before timeout
        :param int tabs: the number of tabs to use as indentation
        """

        verify = 'visibility' if waiting else 'presence'
        self.utils.console("Verifying {} of {} {}...".format(verify, self.item_type, self.name)
                           if message == '' else message, tabs=tabs)
        self._update_reference(timeout=timeout, waiting=waiting, tabs=tabs, force=True)

    def wait_until_visible(self, message='', timeout=None, strict=True, tabs=0):
        """Wait until item is visible. No exceptions should be thrown out for this to pass

        :param str message: the message to display before looking for the element
        :param float timeout: the number of seconds to expire before timeout
        :param bool strict: if True and item is not found, raise an exception
        :param int tabs: the number of tabs to use as indentation
        """

        tabs_plus_one = tabs + 1
        self._update_reference(waiting=True, force=True, tabs=tabs, strict=strict)

        if not strict and not self._reference:
            self.utils.console("{} is already stale for some reason.".format(self.name), tabs=tabs_plus_one)
            return

        try:
            is_displayed = self._reference.is_displayed()
        except StaleElementReferenceException:
            # sometimes, staleness happens so fast it's between update reference and is_displayed call
            if strict:
                raise StaleElementReferenceException("{} is already stale.".format(self.name))
            else:
                is_displayed = False

        if is_displayed:
            self.utils.console("{} is already visible.".format(self.name), tabs=tabs_plus_one)
        else:
            self.utils.start_timer('item_wait_visibility', self.timers)

            if timeout is None:
                timeout = wait.PAGE_TIMEOUT

            if message == '':
                message = "Waiting for {} {} to appear...".format(self.item_type, self.name)

            self.utils.console(message, tabs=tabs)

            try:
                WebDriverWait(self.source.browser, timeout).until(
                    expected_conditions.visibility_of(self._reference))
            except TimeoutException:
                if strict:
                    raise TimeoutException(
                        "Selenium command timed out while checking visibility for {} {} with {}.".format(
                            self.item_type, self.name, self._description))
            except StaleElementReferenceException:
                if strict:
                    raise StaleElementReferenceException(
                        "{} {} with {} is stale.".format(self.item_type, self.name, self._description))
            except NoSuchElementException:
                if strict:
                    raise NoSuchElementException(
                        "{} {} with {} is not found.".format(self.item_type, self.name, self._description))

            self.utils.time_elapsed('item_wait_visibility', self.timers, tabs=tabs_plus_one)

    def wait_until_hidden(self, message='', timeout=None, tabs=0):
        """Wait until item is hidden. No exceptions should be thrown out for this to pass

        :param str message: the message to display before looking for the element
        :param float timeout: the number of seconds to expire before timeout
        :param int tabs: the number of tabs to use as indentation
        """

        self._update_reference(tabs=tabs, force=True)
        self.utils.start_timer('item_wait_visibility', self.timers)
        tabs_plus_one = tabs + 1

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        if message == '':
            message = "Waiting for {} {} to be hidden...".format(self.item_type, self.name)

        self.utils.console(message, tabs=tabs)

        try:
            WebDriverWait(self.source.browser, timeout).until_not(
                expected_conditions.visibility_of(self._reference))
        except TimeoutException:
            self.utils.time_elapsed('item_wait_visibility', self.timers, tabs=tabs_plus_one)
            raise TimeoutException("Selenium command timed out while checking if {} {} with {} is hidden.".format(
                self.item_type, self.name, self._description))

        self.utils.time_elapsed('item_wait_visibility', self.timers, tabs=tabs_plus_one)

    def wait_until_stale(self, message='', timeout=None, tabs=0, update=False, strict=True):
        """Wait until item has turned stale (state changed).

        :param str message: the message to display before looking for the element
        :param float timeout: the number of seconds to expire before timeout
        :param int tabs: the number of tabs to use as indentation
        :param bool strict: if True and item is not found, raise an exception
        :param bool update: if True, update references
        """

        if update:
            self._update_reference(tabs=tabs, force=True)

        self.utils.start_timer('item_stale_remove', self.timers)
        tabs_plus_one = tabs + 1

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        if message == '':
            message = "Waiting for {} {} to be stale...".format(self.item_type, self.name)

        self.utils.console(message, tabs=tabs)

        try:
            WebDriverWait(self.source.browser, timeout).until(expected_conditions.staleness_of(self._reference))
        except TimeoutException:
            if strict:
                self.utils.time_elapsed('item_stale_remove', self.timers, tabs=tabs_plus_one)
                raise TimeoutException("Selenium command timed out while checking if {} {} with {} is stale.".format(
                    self.item_type, self.name, self._description))
        except NoSuchElementException:
            if strict:
                raise TimeoutException(
                    "{} {} with {} is not found.".format(self.item_type, self.name, self._description))

        self.remove_reference()
        self.utils.time_elapsed('item_stale_remove', self.timers, tabs=tabs_plus_one)

    def wait_until_removed(self, message='', timeout=None, tabs=0):
        """Wait until item is removed. No exceptions should be thrown out for this to pass

        :param str message: the message to display before looking for the element
        :param float timeout: the number of seconds to expire before timeout
        :param int tabs: the number of tabs to use as indentation
        """

        tabs_plus_one = tabs + 1
        self._update_reference(tabs=tabs, force=True, strict=False)

        if getattr(self, '_reference', None) is None:
            self.utils.console("{} is not present.".format(self.alias), tabs=tabs_plus_one)
            return

        try:
            self._reference.is_enabled()
        except StaleElementReferenceException:
            self.utils.console("{} is already stale.".format(self.alias), tabs=tabs_plus_one)
            return

        self.utils.start_timer('item_wait_remove', self.timers)

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        self.utils.console("Waiting for {} {} to be removed...".format(self.item_type, self.alias)
                           if message == '' else message, tabs=tabs)

        try:
            WebDriverWait(self.source.browser, timeout).until(expected_conditions.staleness_of(self._reference))
        except TimeoutException:
            self.utils.time_elapsed('item_wait_remove', self.timers, tabs=tabs_plus_one)
            raise TimeoutException("Selenium command timed out while checking if {} {} with {} is gone.".format(
                self.item_type, self.name, self._description))

        the_css_selector = self.parent.css_selector + ' ' + self.css_selector \
            if self.use_parent_css_selector else self.css_selector

        try:
            self.source.browser.find_element_by_css_selector(the_css_selector)
        except NoSuchElementException:
            self.remove_reference()
        else:
            raise StaleElementReferenceException("{} {} still exists!".format(self.item_type, self.name))

        self.utils.time_elapsed('item_wait_remove', self.timers, tabs=tabs_plus_one)

    def show_text(self, update=True):
        """Display the text portion of the item

        :param bool update: if True, runs update_reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Text for {}: {}".format(self.name, self._reference.text))

    def hover(self, message='', update=True):
        """Hover the mouse over the element

        Note: as of 03/16/17, this does not work in firefox browser with geckodriver (marionette)

        :param str message: the message to display before looking for the element
        :param bool update: if True, runs update_reference first
        """

        if update:
            self._update_reference()

        self.source.mouse = webdriver.ActionChains(self.source.browser)
        self.utils.console("Hovering over {} {}...".format(self.item_type, self.name) if message == '' else message)
        self.source.mouse.move_to_element(self._reference).perform()


class OcomTestMixin(Foundation):
    """Mixin Class shared in Ocom test case classes"""

    heading = "---Ocom Test---"
    # The heading text to display on the console once the class instance is loaded
    always_load_country_data = False
    # if True, always load country data on every load_fixture method
    load_fixtures_once = False
    # if True, load fixtures once at the class instance's setup
    fixtures_to_be_loaded = None
    # param list fixtures_to_be_loaded: if value is a list, use that list of JSON files to load
    # (see all_fixtures() method)
    utils = OcomTestUtils()
    # the Test utilities instance

    demo_user = 'demo_user'
    # common username for use in tests"""
    demo_staff = 'demo_staff'
    # common staff username for use in tests"""
    demo_admin = 'demo_admin'
    # common admin username for use in tests"""
    common_password = 'testing123'
    # common password for use in tests"""

    @classmethod
    def _setup_heading(cls):
        """Display heading and set current time to internal start_time whenever an instance of this class initializes"""

        verbosity = 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0

        if verbosity > 0:
            cls.timers['_main_start_'] = datetime.datetime.now()
            utils.console(cls.heading, newlines=1)
            utils.console("Initiating class...", verbosity=verbosity)

    @classmethod
    def _time_elapsed_main(cls):
        """Display the elapsed time from the time the class was initialized until class teardown"""

        if settings.VERBOSE_OCOM_TEST_CLASSES:
            utils.show_time_difference(cls.timers['_main_start_'], datetime.datetime.now(),
                                       message="Total Time elapsed: ", tabs=0)

    @classmethod
    def setup_factory(cls, factory_class):
        cls.factory = factory_class


class OcomTestCaseNoFixtures(TestCase, OcomTestMixin):
    """Special TestCase class with no fixture loading"""

    timers = dict()
    # timers collections for measuring elapsed time among operations
    assertions = asserts.TestAssertions()
    # assertions container

    def setUp(self):
        self.current_url = ''
        self.response = None
        self.utils.console("Initiating method: {}".format(self), newlines=1)

    def tearDown(self):
        self.utils.console("Finished method: {}".format(self))

    @classmethod
    def setUpClass(cls):
        cls._setup_heading()

        try:
            # noinspection PyUnresolvedReferences
            cls.factory.set_utils(utils)
        except AttributeError:
            # it's ok if it does not exist
            pass

        super(OcomTestCaseNoFixtures, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(OcomTestCaseNoFixtures, cls).tearDownClass()
        cls._time_elapsed_main()


class OcomTestCaseClearData(OcomTestCaseNoFixtures):
    """Special TestCase class with country data load per test and one-time fixture loading"""

    load_fixtures_once = True
    always_load_country_data = True

    @classmethod
    def setUpClass(cls):
        super(OcomTestCaseClearData, cls).setUpClass()
        utils.load_fixtures(cls.fixtures_to_be_loaded, clear_db=True, populate_countries=cls.always_load_country_data)


class OcomTestCase(OcomTestCaseNoFixtures):
    """Special TestCase class with conditional fixture loading"""

    always_load_country_data = True

    @classmethod
    def setUpClass(cls):
        super(OcomTestCase, cls).setUpClass()

        if cls.load_fixtures_once:
            utils.load_fixtures(cls.fixtures_to_be_loaded,
                                message="Attempting to load fixtures in this class for once...",
                                populate_countries=cls.always_load_country_data)


class OcomLiveServerTestCaseNoFixtures(StaticLiveServerTestCase, OcomTestMixin):
    """Special LiveTestCase class"""

    start_time = None
    """:param datetime.datetime start_time: the start time"""
    load_fixtures_once = False
    """:param bool load_fixtures_once: if True, load fixtures only once for the class's lifetime"""
    always_reset_display = False
    """:param bool always_reset_display: if True, always resets display for each test setup"""
    always_reset_browser = True
    """:param bool always_reset_browser: if True, always resets browser for each test setup (experimental for False)"""
    always_clear_data = False
    """:param bool always_clear_data: if True, always clears test DB for each test setup"""
    always_load_fixtures = False
    """:param bool always_load_fixtures: if True, always loads fixtures for each test setup

    NOTE: Must do this if you are using Selenium Tests (because LiveServerTestCase is TransactionTestCase)
    """
    clear_data_once = False
    """:param bool clear_data_once: if True, clears test DB during the class instance setup"""
    POLL_FREQUENCY = wait.POLL_FREQUENCY
    """:param float POLL_FREQUENCY: the number of seconds to query for an element status change"""
    WAIT_INTERVAL = wait.WAIT_INTERVAL
    """:param float WAIT_INTERVAL: the number of seconds to wait for an interval to occur (used mostly for messages)"""
    PAGE_TIMEOUT = wait.PAGE_TIMEOUT
    """:param float PAGE_TIMEOUT: the maximum number of seconds to wait for a page to load before timeout occurs"""
    assertions = asserts.LiveServerTestAssertions()
    """:param LiveServerTestAssertions assertions: assertions container"""
    mocks = mocks.HttpMocks()
    """:param tests.mocks.HttpMocks mocks: mocks instance"""

    @classmethod
    def reset_display_once(cls, width=None, height=None):
        """Restart the display once

        :param int width: the screen display width to set (xvfb-dependent)
        :param int height: the screen display height to set (xvfb-dependent)
        """

        verbosity = 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0
        height, width = utils.get_screen_sizes(height, width)
        utils.console("Initializing display resolution from class method: {}x{}".format(height, width),
                      verbosity=verbosity)

        if utils.get_available_browser_type() == utils.PHANTOMJS:
            # we do not need Xvfb
            if getattr(cls, 'browser', None) is None:
                utils.console("Initializing display resolution deferred...", verbosity=verbosity)
            else:
                # noinspection PyUnresolvedReferences
                cls.browser.set_window_size(width, height)
        else:
            cls.display = Xvfb(width=width, height=height)
            cls.display.start()

    @classmethod
    def reset_browser_once(cls, browser_type=None, timeout=None):
        """Restart the browser

        Note: This structure allows cross-browser tests

        :param str or None browser_type: the initial browser type to use; this will be checked against the settings
        (current choice values are None, 'PHANTOMJS', 'FIREFOX' and 'GOOGLE_CHROME')
        :param int timeout: the page load timeout to set
        """

        start_time = datetime.datetime.now()
        verbosity = 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0

        # if no browser selected, check if any are activated and use instead
        if cls.browser is None:
            utils.console("Initializing browser from class method...", verbosity=verbosity)
            cls.browser, cls.browser_type = BROWSER_MAPPER[utils.get_available_browser_type(browser_type)]()
        else:
            cls.browser.quit()
            utils.console("Resetting browser from class method...", verbosity=verbosity)
            cls.browser, cls.browser_type = BROWSER_MAPPER[cls.browser_type]() \
                if browser_type is None else BROWSER_MAPPER[utils.get_available_browser_type(browser_type)]()

        if cls.browser_type == utils.PHANTOMJS:
            height, width = utils.get_screen_sizes()
            utils.console("Initializing display resolution from class method: {}x{}".format(height, width),
                          verbosity=verbosity, tabs=1)
            cls.browser.set_window_size(width, height)

        if cls.browser_type != utils.NO_BROWSER:
            if timeout is None:
                timeout = cls.PAGE_TIMEOUT

            if cls.browser is None:
                utils.console("Attempting to re-load browser...", verbosity=verbosity)
                cls.browser, cls.browser_type = BROWSER_MAPPER[utils.get_available_browser_type(browser_type)]()

            cls.mouse = webdriver.ActionChains(cls.browser)
            cls.browser.set_page_load_timeout(timeout)

        utils.show_time_difference(start_time, datetime.datetime.now(), verbosity=verbosity)

    def reset_display(self, width=None, height=None, shutdown=False):
        """Initialize display and browser objects

        :param int width: width in pixels
        :param int height: height in pixels
        :param bool shutdown: if True, do not initialize display
        """

        if self.browser_type == utils.PHANTOMJS:
            if not shutdown:
                height, width = utils.get_screen_sizes(height, width)
                utils.console("Resetting display to: {}x{}".format(height, width), verbosity=self.utils.verbosity)
                self.browser.set_window_size(width, height)
        elif self.display is None:
            if not shutdown:
                height, width = utils.get_screen_sizes(height, width)
                utils.console("Initializing display: {}x{}".format(height, width), verbosity=self.utils.verbosity)
                self.display = Xvfb(width=width, height=height)
                self.display.start()
        else:
            self.utils.console("Stopping display...")
            self.display.stop()

            if not shutdown:
                height, width = utils.get_screen_sizes(height, width)
                self.addCleanup(self.display.stop)
                utils.console("Resetting display to: {}x{}".format(height, width), verbosity=self.utils.verbosity)
                self.display = Xvfb(width=width, height=height)
                self.display.start()

    def reset_browser(self, browser_type=None, timeout=None, shutdown=False):
        """Restart the browser

        Note: This structure allows cross-browser tests

        :param str browser_type: the initial browser type to use; this will be checked against the settings
        (current choice values are None, 'PHANTOMJS', 'FIREFOX' and 'GOOGLE_CHROME')
        :param int timeout: the page load timeout to set
        :param bool shutdown: if True, do not re-initialize browser
        """

        self.utils.start_timer('browser', self.timers)

        if self.browser is None:
            if shutdown:
                return
            else:
                self.utils.console("Initializing browser...")

            self.browser, self.browser_type = BROWSER_MAPPER[utils.get_available_browser_type(browser_type)]()
        else:
            self.utils.console("Closing browser...")
            self.browser.quit()

            if shutdown:
                return
            else:
                self.utils.console("Resetting browser...")

            self.browser, self.browser_type = BROWSER_MAPPER[self.browser_type]() \
                if browser_type is None else BROWSER_MAPPER[utils.get_available_browser_type(browser_type)]()

        if self.browser_type == utils.PHANTOMJS:
            height, width = utils.get_screen_sizes()
            self.utils.console("Initializing display resolution from class method: {}x{}".format(height, width), tabs=1)
            self.browser.set_window_size(width, height)

        if self.browser_type != utils.NO_BROWSER:
            self.mouse = webdriver.ActionChains(self.browser)

            if timeout is None:
                timeout = self.PAGE_TIMEOUT

            self.browser.set_page_load_timeout(timeout)

        self.utils.time_elapsed('browser', self.timers)

    def color_picker_value(self, element_id, value):
        """Change color picker <input type="color" value>

        :param str element_id: the element id to change value with
        :param str value: the color value in hexadecimal format
        """

        warnings.warn("{} is deprecated".format(self), DeprecationWarning, stacklevel=2)
        self.utils.console("Element ID: #{}; Color value: {}".format(element_id, value), tabs=1)
        self.browser.execute_script('document.getElementById("{}").value = "{}";'.format(element_id, value))

    def tinymce_frame_sendkeys(self, tinymce_element_id, value):
        """Change value of a Tinymce frame input

        :param str tinymce_element_id: the tinymce frame element id
        :param str value: the value to set
        """

        warnings.warn("{} is deprecated".format(self), DeprecationWarning, stacklevel=2)
        self.utils.console("Changing textarea value for id: {}".format(tinymce_element_id), tabs=1)
        self.browser.switch_to.frame(self.browser.find_element_by_id(tinymce_element_id))
        description_box = self.browser.find_element_by_id('tinymce')
        description_box.clear()
        description_box.send_keys(value)
        self.browser.switch_to.default_content()

    def select2_input_change(self, select2_input_id, value, multi_type=False):
        """Change value of a Select2 input dropdown

        :param str select2_input_id: the select2 frame element id
        :param str value: the value to set
        :param bool multi_type: if True, control is a multiple-type selection; defaults to False
        """

        warnings.warn("{} is deprecated".format(self), DeprecationWarning, stacklevel=2)
        self.utils.console("Changing dropdown value for id: ".format(select2_input_id), tabs=1)
        select2_input = self.browser.find_element_by_id(select2_input_id)
        self.browser.execute_script("arguments[0].scrollIntoView(true);", select2_input)
        select2_input.click()

        if multi_type:
            searchbox = self.browser.find_element_by_css_selector('#' + select2_input_id + ' .select2-input')
        else:
            searchbox = self.browser.find_element_by_css_selector('#select2-drop .select2-input')

        searchbox.send_keys(value)
        selected_item = self.browser.find_element_by_css_selector(
            ".select2-drop[style*='display: block'] .select2-results li.select2-result-selectable")
        selected_item.click()

    def setUp(self):
        self.utils.console("Initiating method: {}".format(self), newlines=1)
        super(OcomLiveServerTestCaseNoFixtures, self).setUp()

        if self.always_clear_data:
            self.utils.clear_data()

        if self.always_load_fixtures:
            self.utils.load_fixtures(self.fixtures_to_be_loaded, populate_countries=self.always_load_country_data)

        if self.always_reset_display:
            self.reset_display()

        if self.browser is None:
            self.reset_browser()

        self.assertions.update(test_case=self)
        self._reference_page = None
        self._page_url = ''

    def tearDown(self):
        if self.always_reset_browser and self.browser:
            self.utils.console("Closing browser...")
            self.browser.quit()
            # self.addCleanup(self.browser.quit)
            self.browser_type = None

        self.utils.console("Finished method: {}".format(self))

    @classmethod
    def setUpClass(cls):
        cls._setup_heading()

        try:
            # noinspection PyUnresolvedReferences
            cls.factory.set_utils(utils)
        except AttributeError:
            # it's ok if it does not exist
            pass

        cls.browser = None
        """:param selenium.webdriver.remote.webdriver.WebDriver browser: the browser to use"""
        cls.display = None

        if cls.clear_data_once and not cls.always_clear_data:
            utils.clear_data("Clearing test DB for once...",
                             verbosity=1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0, tabs=0)

        if cls.load_fixtures_once and not cls.always_load_fixtures:
            utils.load_fixtures(cls.fixtures_to_be_loaded,
                                message="Attempting to load fixtures in this class for once...",
                                populate_countries=cls.always_load_country_data)

        if not cls.always_reset_display:
            cls.reset_display_once()

        if not cls.always_reset_browser:
            cls.reset_browser_once()

        super(OcomLiveServerTestCaseNoFixtures, cls).setUpClass()

    # noinspection PyUnresolvedReferences
    @classmethod
    def tearDownClass(cls):
        verbosity = 1 if settings.VERBOSE_OCOM_TEST_CLASSES else 0

        if cls.browser is not None:
            utils.console("Closing browser from class...", verbosity=verbosity)
            cls.browser.quit()

        if not cls.always_reset_display:
            if cls.display is not None:
                utils.console("Stopping display from class...", verbosity=verbosity)
                cls.display.stop()

        super(OcomLiveServerTestCaseNoFixtures, cls).tearDownClass()
        # Selenium 3.0.1 - 'NoneType' object has no attribute 'path'
        cls._time_elapsed_main()


class OcomLiveServerTestCase(OcomLiveServerTestCaseNoFixtures):
    """Special LiveTestCase class with clear data and fixture loading once for the duration of the test

    NOTE: Classes that inherit this usually consolidate tests because fixture loading for such cannot be shared
          amongst other test cases"""

    clear_data_once = True
    load_fixtures_once = True
    always_load_country_data = True


class OcomLiveServerTestCaseAlwaysClear(OcomLiveServerTestCaseNoFixtures):
    """Special LiveTestCase class with clear data and fixture loading for each test method

    NOTE: Classes that inherit this usually consolidate tests because fixture loading for such cannot be shared
          amongst other test cases"""

    always_clear_data = True
    always_load_fixtures = True
    always_load_country_data = True
    load_fixtures_once = False


class OcomLiveServerTestCaseAlwaysLoad(OcomLiveServerTestCaseNoFixtures):
    """Special LiveTestCase class with fixture loading for each test method"""

    always_clear_data = False
    always_load_fixtures = True
    always_load_country_data = True
    clear_data_once = True
    load_fixtures_once = False
