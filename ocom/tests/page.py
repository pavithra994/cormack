"""tests.page.py - Page object model for Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from . import element, container, wait, app, utils


def get_element_text_as_alias(web_element):
    """Use element text as alias

    :param selenium.webdriver.remote.webelement.WebElement web_element: the element to process
    :return:
    :rtype: str, str
    """

    return 'alias', web_element.text


def get_message_type(web_element):
    """Get Message type based on item class

    :param selenium.webdriver.remote.webelement.WebElement web_element: the webElement item with the class property to
    look for
    :return: tuple containing the key and message type
    :rtype: str, str
    """

    item_class = web_element.get_attribute('class')
    message_types = ['error', 'danger', 'success', 'warning', 'info']
    key = 'message_type'

    for message_type in message_types:
        if message_type in item_class:
            return key, message_type

    return key, ''


class SeleniumPage(app.Foundation):
    """Base selenium page class to initialize the page that will be called from all pages"""

    def __init__(self, test_case, **kwargs):
        """SeleniumPage initialization method

        :param tests.ocom.OcomLiveServerTestCaseNoFixtures test_case: the testCase object
        :param str alias: the page alias
        :param float page_timeout: the page timeout in seconds
        :param float poll_frequency: the value check frequency in seconds
        :param float update_interval: the number of seconds to wait until a status update is given
        :param bool angular: if True, signifies that page is angular
        :param str url_path: the url path of the page
        """

        # the testCase object
        self.source = test_case
        # The Test Page utilities instance
        self.utils = test_case.utils

        self.base_url = test_case.live_server_url
        self.page_timeout = kwargs.get('page_timeout', wait.PAGE_TIMEOUT)
        self.poll_frequency = kwargs.get('poll_frequency', wait.POLL_FREQUENCY)
        self.update_interval = kwargs.get('update_interval', wait.WAIT_INTERVAL)
        self.angular_containers = []

        try:
            self.angular = kwargs['angular']
        except KeyError:
            if getattr(self, 'angular', None) is None:
                self.angular = ''

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

        self._page_url = None
        self.reference_page = None
        self.target_url = None
        self.form_setup()

    @property
    def url(self):
        """The page's url

        :return: see above
        :rtype str
        """

        return self.url_path if self.url_path.startswith('http') else self.base_url + self.url_path

    def _unexpected_url(self, message="Expected current url as:"):
        """Display a series of messages re: unexpected URLs

        :param message: the message to display
        """

        self.utils.console(message, tabs=1)
        self.utils.console(self.url, tabs=2)
        self.utils.console("Got:", tabs=1)
        self.utils.console(self.source.browser.current_url, tabs=2)

    def _save_cookies(self):
        """Save existing cookies"""

        self._saved_cookies = self.source.browser.get_cookies()

    def _load_cookies(self, use_script=False):
        """Load saved cookies

        :param bool use_script: Use script loading if True
        """

        if use_script:
            line = ''

            for some_cookie in self._saved_cookies:
                line += "document.cookie = '{name}={value}; path={path}; domain={domain}; expires={expires}';\n".format(
                    **some_cookie)

            if line != '':
                self.source.browser.execute_script(line)
        else:
            [self.source.browser.add_cookie(some_cookie) for some_cookie in self._saved_cookies]

    def _update_control_group(self, container_object, css_selector='', start=0, end=None, item_attribute_adder=None,
                              alias_css_selector=None):
        """Update dynamic controls for a container

        :param tests.container.Container: the container reference to use
        :param str css_selector: if value is not empty. use as CSS selector instead of the one set for the container
        :param int start: the zero-based index to start traversing with
        :param int end: the zero-based index to stop traversing with
        :param function item_attribute_adder: the function reference to add attributes to item
        :param str alias_css_selector: retrieve the content of the element of this CSS selector as alias
        :return: the updated group controls
        :rtype: list
        """

        self.utils.start_timer('update_control_group', self.timers)
        group_container = []
        container_name = container_object.alias
        group_css_selector = container_object.css_selector if css_selector == '' else css_selector

        if alias_css_selector is None and hasattr(container_object, 'alias_css_selector'):
            alias_css_selector = getattr(container_object, 'alias_css_selector')

        self.utils.console("Updating {} controls...".format(container_name))
        self.utils.console("Base CSS selector: {}".format(group_css_selector), tabs=1)
        web_elements = self.source.browser.find_elements_by_css_selector(group_css_selector)
        filtered = web_elements[start:end] if end is not None else web_elements[start:]
        show_attrs = {
            'description': 'Description',
            'message_type': 'Alert Type',
        }
        position = start

        for web_element in filtered:
            position += 1

            if alias_css_selector is None:
                alias = '{} Item {}'.format(container_name, position)
            else:
                alias_element = self.safe_find_element_by_css_selector(web_element, alias_css_selector)
                alias = '{} Item {}'.format(container_name, position) \
                    if alias_element is None \
                    else '{}: {}'.format(container_name, alias_element.get_attribute('textContent'))

            item = container_object(self, alias=alias,
                                    css_selector='{}:nth-of-type({})'.format(group_css_selector, position))
            item.reference = web_element

            if item_attribute_adder is not None:
                if callable(item_attribute_adder):
                    item_attribute_adder = [item_attribute_adder, ]

                # noinspection PyTypeChecker
                for func in item_attribute_adder:
                    key, value = func(web_element)
                    setattr(item, key, value)

            group_container.append(item)
            self.utils.console("Added {}".format(alias), tabs=1)
            self.utils.console("CSS selector: {}".format(item.css_selector), tabs=2)

            for key, value in show_attrs.items():
                if hasattr(item, key):
                    self.utils.console("{}: {}".format(value, getattr(item, key)), tabs=2)

        if not filtered:
            self.utils.console("No elements found.", tabs=1)

        self.utils.time_elapsed('update_control_group', self.timers, tabs=1)
        return group_container

    def _wait_handles(self):
        """Wait for handles to exceed count
        :return: True if handles are greater than the set window count
        :rtype: bool
        """

        return self.source.browser.window_handles > self.window_count

    def stop_load(self, message=''):
        """Attempt to stop loading a page

        :param str message: the message to display
        """

        self.utils.console("Attempting to stop {} from loading...".format(self.alias) if message == '' else message)
        self.source.browser.execute_script("window.stop();")

    def update_controls(self):
        """Internal method for updating controls"""

        pass

    def update_staleness_checks(self):
        """Trigger setting of reference page for staleness/ change checks"""

        self._page_url = self.source.browser.current_url
        self.window_handle = self.source.browser.current_window_handle
        self.reference_page = self.source.browser.find_element_by_tag_name('html')

    def form_setup(self):
        """Additional steps to run (override on derived classes)"""

        raise NotImplemented("Extend this method by adding elements")

    def redirect_tab(self, source_page, absorb_url=False, update_alerts=False, check_ready_state=False):
        """Redirect/move to page url on a new tab/window

        :param SeleniumPage source_page: the originating page
        :param bool absorb_url: if True, the browser's url will be set to the page's url
        :param bool update_alerts: if True, we refresh alerts
        :param bool check_ready_state: if True, we check the DOM ready state
        """

        self.utils.start_timer('wait_tab_load', self.timers)
        self.window_count = len(self.source.browser.window_handles)
        utils.wait_for_function(self._wait_handles, "New tab opened.",
                                prewait=self.source.browser_type == utils.FIREFOX)
        window_handles = []
        window_handles.extend(self.source.browser.window_handles)
        window_handles.remove(source_page.window_handle)
        self.window_handle = window_handles[0]
        self.source.browser.switch_to.window(self.window_handle)

        if absorb_url:
            self.url_path = self.source.browser.current_url.replace(self.base_url, '') \
                if source_page.target_url is None else source_page.target_url

        if absorb_url or self.url in self.source.browser.current_url:
            self.utils.console("Confirmed redirect to {}: ({})".format(self.name, self.url), tabs=1)
            self.reference_page = None
            self._wait_until_page_loaded(self, check_ready_state=check_ready_state)
            self.update_alerts(update_alerts)
            self.update_controls()
            self.source.assertions.update(self)
        else:
            # we intentionally won't run update controls and assertions here so you need to remedy this first
            self._unexpected_url("Expected redirect to:")

        self.utils.time_elapsed('wait_tab_load', self.timers, tabs=1)

    def close_tab(self, return_page):
        """Close current tab and return to tab of specified page

        :param return_page: the page to return to
        """

        page_state = self.source.browser.execute_script('return document.readyState;')

        if page_state != 'complete':
            self.stop_load()

        self.utils.console("Closing browser tab/window and returning to {}...".format(return_page.alias))
        self.source.browser.close()
        self.source.browser.switch_to.window(return_page.window_handle)

    def redirect(self, target_url=None, absorb_url=False, update_alerts=False, update_controls=True):
        """Redirect/move to page url

        :param str or None target_url: the target url of the redirect
        :param bool absorb_url: if True, the browser's url will be set to the page's url
        :param bool update_alerts: if True, we refresh alerts
        :param bool update_controls: if True, update controls
        """

        # TODO: use different logic for absorb url when dealing with angular pages
        if absorb_url or self.angular:
            self.url_path = self.source.browser.current_url.replace(self.base_url, '') \
                if target_url is None else target_url

        if absorb_url or self.angular or self.url in self.source.browser.current_url:
            self.utils.console("Confirmed redirect to {}: ({})".format(self.name, self.url), tabs=1)
            self.update_alerts(update_alerts)

            if update_controls:
                self.update_controls()

            self.source.assertions.update(self)
        else:
            # we intentionally won't run update controls and assertions here so you need to remedy this first
            self._unexpected_url("Expecting redirect to:")

    def redirect_back(self, update_alerts=True, update_controls=True):
        """Redirect back to current page

        :param bool update_alerts: if True, we expect messages to appear on the new page
        :param bool update_controls: if True, update controls
        """

        if self.url in self.source.browser.current_url:
            self.utils.console("Confirmed redirect BACK on {}: ({})".format(self.name, self.url), tabs=1)
            # we may not need to update assertions object here
            # however, we always need to update controls as related items may have been added or removed
            self.update_alerts(update_alerts)

            if update_controls:
                self.update_controls()

            self.source.assertions.update(self, alerts_only=True)
        else:
            # we intentionally won't run update controls here so you need to remedy this first
            self._unexpected_url("Expecting no redirect:")

    def _change_url(self, link, timeout=None, target_url=None, check_staleness=True, check_ready_state=True,
                    skip=False):
        """Proceed to url from browser

        :param str link: the url to go to
        :param float timeout: amount of time in seconds for a timeout to occur during processing
        :param str or None target_url: the target url for mocking
        :param bool check_staleness: if True, check for staleness of page
        :param bool check_ready_state: if True, we check the DOM ready state
        :param bool skip: if True, skip wait
        """

        self.utils.start_timer('url', self.timers)

        # below statement allows self.PAGE_TIMEOUT to be overridden on inherited classes
        if timeout is None:
            timeout = self.page_timeout

        self.utils.console("Changing browser url to: {}".format(link if target_url is None else target_url))

        self._load_page(self, link)
        # self.source.browser.get(link)

        if not skip:
            self._wait_until_page_loaded(self, timeout,
                                         check_staleness=check_staleness, check_ready_state=check_ready_state)

        self.update_staleness_checks()
        self.utils.time_elapsed('url', self.timers, tabs=1)

    def navigate(self, timeout=None, message='', load_cookies=False, target_url=None, update_alerts=False,
                 check_ready_state=False, check_staleness=False, skip=False):
        """Change browser's url to page's url path

        :param None or float timeout: the page timeout to wait before getting a timeout exception
        :param str message: the message to display
        :param str or None target_url: the target url for mocking
        :param bool load_cookies: if True, load previously-saved cookies
        :param bool update_alerts: if True, check if alerts are present
        :param bool check_staleness: if True, check for staleness of page
        :param bool check_ready_state: if True, we check the DOM ready state
        :param bool skip: if True, we skip the page loaded check
        """

        if load_cookies:
            self.utils.console("Navigating to some page in order to reload cookies...")
            self._change_url(self.base_url + '/about/terms/', timeout, check_staleness=False, check_ready_state=False)
            self._load_cookies(self.is_browser_phantomjs)
            self.refresh(check_staleness=False, check_ready_state=False)

        self.utils.console(message)
        self._change_url(self.url, timeout, target_url, check_ready_state=check_ready_state,
                         check_staleness=check_staleness, skip=skip)
        self.update_controls()
        self.update_alerts(messages_expected=update_alerts)
        self.source.assertions.update(self)

    def save_html(self, filename_without_path, message='', check_path=True, prettify=True):
        """Save html dump of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: The base filename without the absolute path
        :param str message: The message to display
        :param bool check_path: if True, check path with url property
        :param bool prettify: if True, prettifies html
        """

        if check_path and self.url_path not in self.source.browser.current_url:
            self._unexpected_url()
        else:
            message = "Saving html of {}: {}".format(self.alias, filename_without_path) if message == '' else message
            utils.save_html(filename_without_path, self.source.browser.page_source, message, prettify=prettify)

    def save_screenshot(self, filename_without_path, message='', check_path=True, quality=60):
        """Save screenshot of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: filename, without path
        :param str message: The message to display
        :param bool check_path: if True, check path with url property
        :param int quality: If saving as JPEG, the compression quality (higher is better)
        """

        if check_path and self.url_path not in self.source.browser.current_url:
            self._unexpected_url()
        else:
            message = "Taking screenshot file of {}: {}".format(self.alias, filename_without_path) \
                if message == '' else message
            utils.save_screenshot(filename_without_path, self.source.browser, message, quality=quality)

    def scroll_to(self, x, y):
        """Scroll browser window to the given coordinates

        :param int x: scroll to horizontal location
        :param int y: scroll to vertical location
        """

        self.utils.console("Scrolling browser to: {}, {}".format(x, y))
        self.source.browser.execute_script('window.scrollTo({}, {});'.format(x, y))

    def scroll_to_top(self):
        """Scroll browser window to the top"""

        self.utils.console("Scrolling browser to top...")
        self.source.browser.execute_script('window.scrollTo(0, 0);')

    def scroll_to_bottom(self, x=0):
        """Scroll browser window to the bottom

        :param int x: scroll to horizontal location
        """

        self.utils.console("Scrolling browser to bottom...")
        self.source.browser.execute_script('window.scrollTo({}, {});'.format(x, 'document.body.scrollHeight'))

    def resize_browser(self, width, height, message=''):
        """Resize browser dimensions

        :param int width: the new browser width
        :param int height: the new browser height
        :param str message: the message to display
        """

        self.utils.console("Setting browser size to {}x{}...".format(width, height) if message == '' else message)
        self.source.browser.set_window_size(width, height)

    def clear_all_cookies(self, message="Removing all cookies from browser..."):
        """Remove all browser cookies

        :param str message: the message to display
        """

        self.utils.console(message)
        self.source.browser.delete_all_cookies()

    def update_alerts(self, messages_expected=False):
        """Update alert controls

        :param bool messages_expected: if True, update alerts from control group; otherwise, clear alerts
        """

        if messages_expected:
            self.alerts = self._update_control_group(container.Alert, item_attribute_adder=get_message_type)
        else:
            self.alerts = []
            self.utils.console("Skipped update for alerts.", tabs=1)

    def refresh(self, message='', update_alerts=False, update_controls=True, check_ready_state=True,
                check_staleness=True, timeout=None):
        """Refresh the browser

        :param str message: the message to display
        :param bool update_alerts: if True, we refresh alerts
        :param bool update_controls: if True, we refresh controls
        :param bool check_staleness: if True, check for staleness of page
        :param bool check_ready_state: if True, we check the DOM ready state
        :param float timeout: the delay to wait
        """

        self.utils.start_timer('browser_refresh', self.timers)
        self.utils.console(message)
        self.utils.console("Refreshing browser at url: {}".format(self.source.browser.current_url))
        self.source.browser.refresh()
        self._wait_until_page_loaded(self, self.page_timeout, check_ready_state=check_ready_state,
                                     check_staleness=check_staleness)

        if timeout:
            self._wait_until_timeout(timeout)

        if update_controls:
            self.update_controls()

        self.utils.time_elapsed('browser_refresh', self.timers, tabs=1)
        # we do statement below later so we can see the time elapsed for above
        self.update_alerts(messages_expected=update_alerts)
        self.source.assertions.update(self, alerts_only=True)

    def restart_browser(self, save_cookies=True):
        """Restart the browser

        :param bool save_cookies: if True, save current cookies
        """

        if save_cookies:
            self._save_cookies()

        self.source.reset_browser() if self.source.always_reset_browser else self.source.reset_browser_once()


class CommonPage(SeleniumPage):
    """Common Page for both dashboard and standard pages"""

    def form_setup(self):
        """Common Page controls"""

        self.alerts = []


class StandardPage(CommonPage):
    """Standard Page with navigation bar and footer"""

    def __init__(self, test_case, update_footer=False, **kwargs):
        """SeleniumPage initialization method

        :param tests.ocom.OcomLiveServerTestCaseNoFixtures test_case: the testCase object
        :param bool update_footer: if True, automatically update footer links on redirect or refresh
        :param str alias: the page alias
        :param float page_timeout: the page timeout in seconds
        :param float poll_frequency: the value check frequency in seconds
        :param float update_interval: the number of seconds to wait until a status update is given
        :param str url_path: the url path of the page
        """

        self.update_footer = update_footer
        super(StandardPage, self).__init__(test_case, **kwargs)

    def form_setup(self):
        """Standard Page elements here"""

        super(StandardPage, self).form_setup()
        self.logo = element.ImageLink(self, css_selector='div.middle > img', alias='Logo')

    def update_controls(self):
        """Standard Page dynamic controls update"""

        super(StandardPage, self).update_controls()
        if self.angular and self.angular_containers:
            for container_id in self.angular_containers:
                if hasattr(self, container_id):
                    item = getattr(self, container_id)
                    item.remove_reference()
                    self.utils.console("Cleared reference for container {}".format(item.name), tabs=1)

        """
        if not self.fixed_categories:
            # find menus
            self.categories_menu.menus = []
            container_name = self.categories_menu.alias
            group_css_selector = self.categories_menu.menu_css_selector
            subgroup_css_selector = 'ul > li'

            self.utils.console("Updating {} controls...".format(container_name))
            self.utils.console("Parent CSS selector: {}".format(group_css_selector), tabs=1)
            web_elements = self.source.browser.find_elements_by_css_selector(group_css_selector)
            filtered = web_elements[1:]
            position = 1
            index = 0

            for web_element in filtered:
                position += 1
                main_css_selector = '{}:nth-of-type({})'.format(group_css_selector, position)
                main_css_selector_link = main_css_selector + ' > a'
                actual_item = self.source.browser.find_element_by_css_selector(main_css_selector_link)
                alias = '{} Item {}: {}'.format(container_name, position, actual_item.text)
                item = element.TopMenuLink(self, alias=alias, css_selector=main_css_selector_link)
                item._reference = actual_item
                self.categories_menu.menus.append(item)
                self.utils.console("Added {}".format(alias), tabs=1)
                self.utils.console("CSS selector: {}".format(item.css_selector), tabs=2)
                self.utils.console("Index: {}".format(index), tabs=2)
                index += 1
                # find submenus
                sub_elements = web_element.find_elements_by_css_selector(subgroup_css_selector)
                sub_position = 0

                for _ in sub_elements:
                    sub_position += 1
                    sub_css_selector = '{} > {}:nth-of-type({}) > a'.format(main_css_selector, subgroup_css_selector,
                                                                            sub_position)
                    actual_sub_item = self.source.browser.find_element_by_css_selector(sub_css_selector)
                    sub_alias = '{}->Sub-item {}: {}'.format(alias, sub_position,
                                                             actual_sub_item.get_attribute('textContent'))
                    sub_item = element.SubMenuLink(self, alias=sub_alias, css_selector=sub_css_selector)
                    sub_item._reference = actual_sub_item
                    self.categories_menu.menus.append(sub_item)
                    self.utils.console("Added {}".format(sub_alias), tabs=1)
                    self.utils.console("CSS selector: {}".format(sub_item.css_selector), tabs=2)
                    self.utils.console("Index: {}".format(index), tabs=2)
                    index += 1

            if not filtered:
                self.utils.console("No elements found.", tabs=1)
        """

    def fillup(self, data):
        """Fill-up form input with provided data"""

        # TODO: use mapper
        for key, value in data.items():
            if hasattr(self, key):
                the_element = getattr(self, key)
                if isinstance(the_element, element.TextBox):
                    the_element.input(value)
                elif isinstance(the_element, element.DropDown):
                    the_element.select(value)
                elif isinstance(the_element, element.CheckBox):
                    if value:
                        the_element.check()
                    else:
                        the_element.uncheck()
                # TODO: image

    def fillup_form_with_blanks(self, fields, update=True):
        """Attempt to remove required form attributes and fill up form with blank data

        :param list fields: field names to remove required from and fill with blanks
        :param bool update: if True, update input field's reference
        """

        for field in fields:
            if hasattr(self, field):
                the_element = getattr(self, field)
                if isinstance(the_element, element.TextBox):
                    the_element.remove_required()
                    the_element.input('', update=update)
                elif isinstance(the_element, element.DropDown):
                    the_element.remove_required()
                    the_element.select('', update=update)


class HomePage(StandardPage):
    """The main page"""

    alias = 'Home Page'

    def __init__(self, test_case, update_footer=False, update_sections=False, **kwargs):
        """SeleniumPage initialization method

        :param tests.ocom.OcomLiveServerTestCaseNoFixtures test_case: the testCase object
        :param bool update_footer: if True, automatically update footer links on redirect or refresh
        :param bool update_sections: if True, automatically update homepage sections on redirect or refresh
        :param str alias: the page alias
        :param float page_timeout: the page timeout in seconds
        :param float poll_frequency: the value check frequency in seconds
        :param float update_interval: the number of seconds to wait until a status update is given
        :param str url_path: the url path of the page
        """

        self.update_sections = update_sections
        super(HomePage, self).__init__(test_case, update_footer=update_footer,
                                       **kwargs)

    def form_setup(self):
        """HomePage controls"""

        super(HomePage, self).form_setup()
        self.loading_bar = element.Spinner(self, dom_id='loading-bar-spinner', alias='Loading Bar Spinner')


class SignupPage(StandardPage):
    """Signup/Registration page"""

    url_path = '/accounts/signup/'
    alias = 'Registration Page'

    def form_setup(self):
        """SignupPage controls"""

        super(SignupPage, self).form_setup()
        self.username = element.TextBox(self, name='username', alias='Username Textbox')
        self.email = element.TextBox(self, name='email', alias='E-mail Textbox')
        self.password1 = element.TextBox(self, name='password1', alias='Password Textbox')
        self.password2 = element.TextBox(self, name='password2', alias='Confirm Password Textbox')
        self.captcha_label = element.Label(self, css_selector='label[for=id_captcha]', alias='Captcha Form Label')
        self.submit = element.Button(self, css_selector='button[name=registration_submit]', alias='Submit Button')
        # oauth
        self.facebook = element.Link(self, css_selector='.login.fb.btn', alias='Register with Facebook Button')
        self.google = element.Link(self, css_selector='.login.gplus.btn', alias='Register with Google+ Button')

    def register(self, username, email, password1, password2, link_should_change=True, timeout=None):
        """Input new account credentials and submit

        :param str username: account name
        :param str email: account email
        :param str password1: account password
        :param str password2: account confirm password
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        """

        self.username.input(username)
        self.email.input(email)
        self.password1.input(password1)
        self.password2.input(password2)
        self.submit.click(link_should_change=link_should_change, timeout=timeout)


class SignupDonePage(StandardPage):
    """Signup/Registration done page"""

    url_path = '/signup/complete/'
    alias = 'Registration Complete Page'

    def form_setup(self):
        """SignupDonePage controls"""
        super(SignupDonePage, self).form_setup()
        self.acknowledge = element.Caption(self, alias='Registration Acknowledgement Text', css_selector='p.registered')


class SigninPage(StandardPage):
    """Sign-in / Login page"""

    url_path = '/accounts/signin/'
    alias = 'Login Page'

    def form_setup(self):
        """Sign-in Page controls"""

        super(SigninPage, self).form_setup()
        # either username or email can be used here
        self.identification = element.TextBox(self, name='identification', alias='Username/E-mail Textbox')
        self.password = element.TextBox(self, name='password', alias='Password Textbox')
        self.submit = element.Button(self, css_selector='button[name=login_submit]', alias='Login Button')

    def login(self, identification, password, link_should_change=True, timeout=None):
        """Input new account credentials and submit

        :param str identification: account name or email
        :param str password: account password
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        """

        self.identification.input(identification)
        self.password.input(password)
        self.submit.click(link_should_change=link_should_change, timeout=timeout)


class SignoutPage(StandardPage):
    """Sign-out/Logout page"""

    url_path = '/accounts/signout/'
    alias = 'Logout Page'

    def form_setup(self):
        """Sign-out/Logout page controls"""

        super(SignoutPage, self).form_setup()
        # either username or email can be used here
        self.message = element.Caption(self, class_name='signed-out', alias='Sign Out Text')


class AccountSidebarPage(StandardPage):
    """Account with Sidebar page"""

    def form_setup(self):
        """Account with Sidebar controls"""

        super(AccountSidebarPage, self).form_setup()
        # either username or email can be used here
        self.sidebar = container.ProfileSidebar(self)


class AccountProfilePage(AccountSidebarPage):
    """Account Profile page"""

    url_path = '/accounts/profile/'
    alias = 'Account Profile Page'

    def form_setup(self):
        """Account Profile page controls"""

        super(AccountProfilePage, self).form_setup()
        # either username or email can be used here
        self.change_password = element.Link(self, css_selector='.content a.password',
                                            alias='Change Password Button')
        self.edit = element.Link(self, css_selector='.content a.edit', alias='Edit Profile Button')
        self.delete = element.Link(self, css_selector='.content a.delete', alias='Delete Profile Button')


class EditProfilePage(AccountSidebarPage):
    """Account Profile edit page"""

    url_path = '/accounts/profile/edit/'
    alias = 'Account Edit Profile Page'

    def form_setup(self):
        """Account profile edit page controls"""

        super(EditProfilePage, self).form_setup()
        self.first_name = element.TextBox(self, name='first_name', alias='First Name Textbox')
        self.last_name = element.TextBox(self, name='last_name', alias='Last Name Textbox')
        """
        self.mugshot = element.CoopitaImage(self, name='mugshot', delete_css_selector='button.btn-dump',
                                            hidden_checkbox=False, alias='Mugshot Image')
        """
        self.privacy = element.DropDown(self, name='privacy', alias='Privacy Dropdown')
        self.gender = element.DropDown(self, name='gender', alias='Gender Dropdown')
        self.edit_email = element.CheckBox(self, name='edit_email', visible_css_selector='label[for=id_edit_email]',
                                           alias='Edit E-mail Checkbox')
        self.email = element.TextBox(self, name='email', alias='E-mail Textbox')
        self.password = element.TextBox(self, name='password', alias='Password Textbox')
        self.save = element.Button(self, css_selector='#profile_form button[type=submit]', alias='Save Button')
        self.cancel = element.Link(self, css_selector='#profile_form .btn-cancel', alias='Cancel Button')

    def change_email(self, new_email, password, click_edit=True, link_should_change=True):
        """Change e-mail address from account profile. E-mail is changed if correct password is given

        :param str new_email: the new e-mail to set
        :param str password: the account password
        :param bool click_edit: If True, check on edit e-mail to make the e-mail change controls appear
        :param bool link_should_change: If True, browser url should change if clicked
        """

        if click_edit:
            self.edit_email.check()
            self.email.wait_until_visible()

        self.email.input(new_email)
        self.password.input(password)
        self.save.click(link_should_change=link_should_change)


class ChangePasswordPage(AccountSidebarPage):
    """Change Password page"""

    url_path = '/accounts/change-password/'
    alias = 'Account Profile Change Password Page'

    def form_setup(self):
        """Change Password Page controls"""

        super(ChangePasswordPage, self).form_setup()
        # either username or email can be used here
        self.new_password = element.TextBox(self, name='new_password1', alias='New Password Textbox')
        self.new_password_confirm = element.TextBox(self, name='new_password2', alias='Confirm New Password Textbox')
        self.old_password = element.TextBox(self, name='old_password', alias='Old Password Textbox')
        self.save = element.Button(self, css_selector='#change_password_form button[type=submit]', alias='Save Button')
        self.forgot_password = element.Button(self, css_selector='a.btn-primary', alias='Forgot Password Button')
        self.cancel = element.Link(self, css_selector='#change_password_form .btn-cancel', alias='Cancel Button')

    def change_password(self, new_password1, new_password2, old_password, link_should_change=True, timeout=None):
        """Input change password fields and save

        :param new_password1: the new password to set
        :param new_password2: confirm the new password. must be equal to new_password1
        :param old_password: the old password
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        """

        self.new_password.input(new_password1)
        self.new_password_confirm.input(new_password2)
        self.old_password.input(old_password)
        self.save.click(link_should_change=link_should_change, timeout=timeout)


class ForgotPasswordPage(AccountSidebarPage):
    """Forgot Password page"""

    url_path = '/accounts/password/reset/'
    alias = 'Account Profile Forgot Password Page'

    def form_setup(self):
        """Forgot Password page controls"""

        super(ForgotPasswordPage, self).form_setup()
        self.email = element.TextBox(self, name='email', alias='E-mail Textbox')
        self.send_password_link = element.Button(self, css_selector='#login_form button[type=submit]',
                                                 alias='Send Password Button')
        self.cancel = element.Link(self, css_selector='#login_form .btn-cancel', alias='Cancel Button')


class DeleteProfilePage(AccountSidebarPage):
    """Delete Profile page"""

    url_path = '/accounts/profile/delete/'
    alias = 'Account Profile Delete Page'

    def form_setup(self):
        """Delete Profile page controls"""

        super(DeleteProfilePage, self).form_setup()
        # either username or email can be used here
        self.password = element.TextBox(self, name='password', alias='Password Textbox')
        self.delete = element.Button(self, css_selector='#delete_profile_form button[type=submit]',
                                     alias='Delete Button')
        self.cancel = element.Link(self, css_selector='#delete_profile_form .btn-cancel', alias='Cancel Button')

    def confirm(self, password, link_should_change=True, timeout=None):
        """Input change password fields and save

        :param password: the account password
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        """

        self.password.input(password)
        self.delete.click(link_should_change=link_should_change, timeout=timeout)


class BeAMerchantPage(StandardPage):
    """Be A Merchant Page"""

    url_path = '/accounts/beamerchant/'
    alias = 'Be A Merchant Page'

    def form_setup(self):
        """Be A Merchant Page controls"""

        super(BeAMerchantPage, self).form_setup()
        self.shop_name = element.TextBox(self, name='shopname', alias='Shop Name Textbox')
        self.shop_description = element.TextArea(self, dom_id='id_description', alias='Description TextArea')
        self.return_policy = element.TextArea(self, name='return_policy', alias='Return Policy TextArea')
        self.website = element.TextBox(self, name='lookbook', alias='Website / Samples Textbox')
        self.paypal_email = element.TextBox(self, name='paypal_email', alias='Paypal E-mail Textbox')
        self.confirm_email = element.TextBox(self, name='confirm_email', alias='Confirm E-mail Textbox')
        self.market_survey = element.DropDown(self, name='market_survey', alias='Market Survey Dropdown')
        self.experience_survey = element.DropDown(self, name='exp_survey', alias='Experience Dropdown')
        self.tos_agreement = element.CheckBox(self, name='tos_agreement',
                                              visible_css_selector='label[for=id_tos_agreement]',
                                              alias='TOS Agreement Checkbox')
        self.signup = element.Button(self, css_selector='#be_a_merchant_form button[type=submit]',
                                     alias='Signup Button')


class AccountProfileBeAMerchantPage(AccountSidebarPage, BeAMerchantPage):
    """Be A Merchant Page for Account Profile"""

    alias = 'Account Profile Be A Merchant Page'

    def form_setup(self):
        """Be A Merchant Page controls"""
        super(AccountProfileBeAMerchantPage, self).form_setup()


class BeAMerchantConfirmationPage(StandardPage):
    """Be A Merchant Confirmation Page"""

    url_path = '/accounts/beamerchantok/'
    alias = 'Be A Merchant Confirmation Page'

    def form_setup(self):
        """Be A Merchant Confirmation Page"""

        super(BeAMerchantConfirmationPage, self).form_setup()
        self.signup = element.Link(self, dom_id='merchant_signup', alias='Login Link')


class AccountProfileBeAMerchantConfirmationPage(BeAMerchantConfirmationPage):
    """Be A Merchant Confirmation Page for Account Profile"""

    alias = 'Account Profile Be A Merchant Confirmation Page'

    def form_setup(self):
        """Be A Merchant confirmation page controls"""

        super(AccountProfileBeAMerchantConfirmationPage, self).form_setup()


class AdminPage(SeleniumPage):
    """Django Admin page"""

    url_path = '/admin/'
    alias = 'Django Admin Page'

    def form_setup(self):
        """Django admin page controls"""

        self.site_name = element.Link(self, dom_id='site-name', alias='Site Label Link')


class ActivationPage(AccountSidebarPage):
    """Account Activation Page"""

    alias = 'Account Profile Activation Page'

    def set_activation_key(self, key):
        """Convenience function to set activation key onto url path

        :param str key: the activation key
        """

        self.url_path = key


class CheckoutPage(StandardPage):
    """General Checkout Page"""

    def form_setup(self):
        """General Checkout Page controls"""

        self.step_1 = element.Link(self, alias='Step One Link', css_selector='li.step.one > a')
        self.step_1_active = element.Caption(self, alias='Step One (Active)',
                                             css_selector='li.step.one.active')
        self.step_2 = element.Link(self, alias='Step Two Link', css_selector='li.step.two > a')
        self.step_2_active = element.Caption(self, alias='Step Two (Active)',
                                             css_selector='li.step.two.active')
        self.step_2_disabled = element.Caption(self, alias='Step Two (Disabled)',
                                               css_selector='li.step.two.disabled')
        self.step_3 = element.Link(self, alias='Step Three Link', css_selector='li.step.three > a')
        self.step_3_active = element.Caption(self, alias='Step Three (Active)',
                                             css_selector='li.step.three.active')
        self.step_3_disabled = element.Caption(self, alias='Step Three (Disabled)',
                                               css_selector='li.step.three.disabled')
        self.step_4_active = element.Caption(self, alias='Step Four (Active)',
                                             css_selector='li.step.four.active')
        self.step_4_disabled = element.Caption(self, alias='Step Four (Disabled)',
                                               css_selector='li.step.four.disabled')
        self.step_5_disabled = element.Caption(self, alias='Step Five (Disabled)',
                                               css_selector='li.step.five.disabled')


class CheckoutAddressPage(CheckoutPage):
    """Step One: Checkout Address Page"""

    url_path = '/checkout/shipping-address/'
    alias = 'Checkout Address Page (Step One)'

    def form_setup(self):
        """Checkout Address controls"""

        super(CheckoutAddressPage, self).form_setup()
        self.title = element.DropDown(self, alias='Title Dropdown', name='title')
        self.first_name = element.TextBox(self, alias='First Name TextBox', name='first_name')
        self.last_name = element.TextBox(self, alias='Last Name TextBox', name='last_name')
        self.address_line1 = element.TextBox(self, alias='Address (Line 1) TextBox', name='line1')
        self.address_line2 = element.TextBox(self, alias='Address (Line 2) TextBox', name='line2')
        self.address_line3 = element.TextBox(self, alias='Address (Line 3) TextBox', name='line3')
        self.city = element.TextBox(self, alias='City TextBox', name='line4')
        self.state = element.TextBox(self, alias='State/County TextBox', name='state')
        self.post_code = element.TextBox(self, alias='Zip/Postcode TextBox', name='postcode')
        self.country = element.DropDown(self, alias='Country Dropdown', name='country')
        self.phone = element.TextBox(self, alias='Phone Number TextBox', name='phone_number')
        self.instructions = element.TextArea(self, alias='Instructions TextArea', name='notes')
        self.cart = element.Link(self, alias='Return to Cart Link',
                                 css_selector='#new_shipping_address .button-group a:nth-child(1)')
        self.proceed = element.Button(self, alias='Continue (Step 2) Button',
                                      css_selector='#new_shipping_address button[type=submit]')
        # TODO: address book


class CheckoutShippingMethodPage(CheckoutPage):
    """Step Two: Shipping Methods Page"""

    url_path = '/checkout/shipping-method/'
    alias = 'Shipping Methods Page (Step Two)'

    def form_setup(self):
        """Checkout Shipping Method controls"""

        super(CheckoutShippingMethodPage, self).form_setup()
        self.items = []
        self.back = element.Link(self, alias='Return to Shipping Address',
                                 css_selector='form.orders a.btn-cancel')
        self.proceed = element.Button(self, alias='Continue (Step 3) Button',
                                      css_selector='form.orders button[type=submit]')

    def update_controls(self):
        """Update controls for Shipping Methods Page"""

        super(CheckoutShippingMethodPage, self).update_controls()
        # self.items = self._update_control_group(container.BasketShippingLineBar)


class CheckoutPaymentDetailsPage(CheckoutPage):
    """Step Three: Payment Details Page"""

    url_path = '/checkout/payment-details/'
    alias = 'Payment Details Page (Step Three)'

    def form_setup(self):
        """Checkout Shipping Method controls"""

        super(CheckoutPaymentDetailsPage, self).form_setup()
        self.back = element.Link(self, alias='Return to Shipping Methods',
                                 css_selector='#checkout a.btn-cancel')
        self.proceed = element.Button(self, alias='Continue (Step 4) Button',
                                      css_selector='#checkout button[type=submit]')


class CheckoutPreviewPage(CheckoutPage):
    """Step Four: Checkout Preview Page"""

    url_path = '/checkout/preview/'
    alias = 'Order Preview Page (Step Four)'

    def form_setup(self):
        """Checkout Shipping Method controls"""

        super(CheckoutPreviewPage, self).form_setup()
        self.back = element.Link(self, alias='Return to Payment Details',
                                 css_selector='#place_order_form a.btn-cancel')
        self.proceed = element.Button(self, alias='Place Order (Step 5) Button',
                                      css_selector='#place_order_form button[type=submit]')
        self.shipping_change = element.Link(self, alias='Change Shipping Methods Link',
                                            css_selector='a.shipping')
        self.payment_change = element.Link(self, alias='Change Payment Details Link',
                                           css_selector='a.payment')
        self.edit_order = element.Link(self, alias='Edit Order Contents Link', css_selector='a.order')
        self.add_voucher = element.Button(self, alias='Add Voucher Button', button_type='button',
                                          css_selector='#voucher_form_link > a')


class ThankYouPage(StandardPage):
    """Step 5: Thank You Page"""

    url_path = '/checkout/thank-you/'
    alias = 'Thank You Page (Step Five)'

    def form_setup(self):
        """Thank You Page controls"""

        super(ThankYouPage, self).form_setup()
        self.order_id = element.Link(self, alias='Order ID Link', dom_id='order_id')
        self.payment_reference = element.Caption(self, alias='Payment Reference Text',
                                                 css_selector='.pay-details strong')


class WishlistsPage(AccountSidebarPage):
    """Wishlists Page"""

    url_path = '/accounts/wishlists/'
    alias = 'Wishlists Page'

    def form_setup(self):
        """Wishlists Page controls"""

        super(WishlistsPage, self).form_setup()
        self.wishlists = []
        self.create = element.Link(self, alias="Create New Wishlist", dom_id='new_wishlist')

    def update_controls(self):
        """Update controls for Wishlists Index"""

        super(WishlistsPage, self).update_controls()
        # self.wishlists = self._update_control_group(container.WishlistRow)


class WishlistCreatePage(AccountSidebarPage):
    """Wishlists Creation Page"""

    url_path = '/accounts/wishlists/create/'
    alias = 'Create New Wishlist Page'

    def form_setup(self):
        """Wishlists Page controls"""

        super(WishlistCreatePage, self).form_setup()
        self.wishlist_name = element.TextBox(self, alias="Wishlist Name", name='name')
        self.save = element.Button(self, alias="Save Button", css_selector='form.profile button[type=submit]')
        self.cancel = element.Link(self, alias="Cancel Button", css_selector='form.profile .btn-cancel')


class WishlistDetailPage(AccountSidebarPage):
    """Wishlist Detail Page"""

    alias = 'Wishlist Detail Page'

    def form_setup(self):
        """Wishlist Detail Page controls"""

        super(WishlistDetailPage, self).form_setup()
        self.update = element.Button(self, alias="Update Quantities Button",
                                     css_selector='form.wishlist button[type=submit]')
        self.empty = element.Link(self, alias="Product Catalogue Link (Empty Notice)", css_selector="a.empty")
        self.wishlists = []
        self.move_to = []

    def update_controls(self):
        """Update controls for Wishlists Details"""

        super(WishlistDetailPage, self).update_controls()
        # self.wishlists = self._update_control_group(container.WishlistDetailRow)
        self.move_to = self._update_control_group(container.DropdownLinks, 'form.wishlist ul.dropdown-menu > li', 1)


class WishlistDetailDeleteConfirmPage(AccountSidebarPage):
    """Wishlist Detail Delete Confirm Page"""

    alias = 'Wishlist Detail Delete Confirm Page'

    def form_setup(self):
        """Wishlist Detail Delete ConfirmPage controls"""

        super(WishlistDetailDeleteConfirmPage, self).form_setup()
        self.remove = element.Button(self, css_selector='form.profile button[type=submit]', alias='Remove Button')
        self.cancel = element.Link(self, css_selector='form.profile a.btn-cancel', alias='Cancel Button')


class BaseCataloguePage(StandardPage):
    """Base Catalogue Page"""

    def form_setup(self):
        """General Catalogue Page controls"""

        super(BaseCataloguePage, self).form_setup()
        self.catalogue_sidebar = container.CatalogueSidebar(self)
        self.product_type_sidebar = container.ProductTypeSidebar(self)
        # self.country_sidebar = container.OriginCountrySidebar(self)
        self.rating_sidebar = container.RatingSidebar(self)
        # self.price_range_sidebar = container.PriceRangeSidebar(self)
        self.no_products = element.Caption(self, alias='No Products message', css_selector='p.no-products')
        self.products = []
        self.sort_by_popper = element.Button(self, button_type='button', alias='Sort By (Popper)', dom_id='id_sort_by')
        self.sort_by = element.DropDown(self, alias='Sort By', css_selector='.sorter ul')
        self.previous_page_span = element.Caption(self, alias='Previous Page Span',
                                                  css_selector='ul.pager > li.previous > span')
        self.previous_page_link = element.Link(self, alias='Previous Page Link',
                                               css_selector='ul.pager > li.previous > a')
        self.current_page_span = element.Caption(self, alias='Current Page Span',
                                                 css_selector='ul.pager > li.active > span')
        self.next_page_span = element.Caption(self, alias='Next Page Span',
                                              css_selector='ul.pager > li.next > span')
        self.next_page_link = element.Link(self, alias='Next Page Link', css_selector='ul.pager > li.next > a')

    def update_controls(self):
        """Update controls for Catalogue Index"""

        super(BaseCataloguePage, self).update_controls()
        # self.products = self._update_control_group(container.ProductPod)


class CataloguePage(BaseCataloguePage):
    """Catalogue Page"""

    def form_setup(self):
        """General Catalogue Page controls"""

        super(CataloguePage, self).form_setup()
        self.show_sidebar = element.Button(self, button_type='button', alias='Toggle Sidebar',
                                           dom_id='show-left-sidebar')
        self.hide_sidebar = element.Button(self, button_type='button', alias='Toggle Sidebar',
                                           dom_id='hide-left-sidebar')


class CatalogueIndexPage(CataloguePage):
    """Catalogue Index Page"""

    url_path = '/catalogue/'
    alias = 'Catalogue Index Page'


class CatalogueRecentPage(CatalogueIndexPage):
    """Catalogue Recently Added Page"""

    url_path = '/catalogue/recently-added/'
    alias = 'Catalogue->Recently Added Page'


class CatalogueMenuPage(CatalogueIndexPage):
    """Catalogue->Menu Page"""

    alias = 'Catalogue->[Menu] Page'


class CatalogueDetailPage(StandardPage):
    """Catalogue Detail Page"""

    alias = 'Catalogue Detail Page'

    def form_setup(self):
        """Catalogue Detail Page controls"""

        super(CatalogueDetailPage, self).form_setup()
        self.magnifying_lens = element.Element(self, alias='Magnifying Lens', css_selector='.magnify .magnify-lens')
        self.gallery_slide_left = element.LinkButton(self, alias='Gallery Slide to Previous Image',
                                                     css_selector='.thumbnail a.left')
        self.gallery_slide_right = element.LinkButton(self, alias='Gallery Slide to Next Image',
                                                      css_selector='.thumbnail a.right')
        self.gallery_images = []
        self.active_gallery_images = []
        self.gallery_thumbnail = []
        self.variants = element.DropDown(self, alias='Product Variants Dropdown', dom_id='product_variants')
        self.price = element.Caption(self, alias='Product Price', css_selector='.product_main .price_color')
        self.sold_out = element.Caption(self, alias='Sold Out Message', css_selector='span.outofstock')
        self.unshippable = element.Caption(self, alias='Unshippable Message', css_selector='span.unshippable')
        self.convert = element.DropDown(self, alias='Currency Conversion Dropdown', dom_id='convert_currencies')
        self.converted_price = dict()
        self.converted_price_bare = element.Caption(self, alias='Price Converted', dom_id='currency_info')
        self.other_products = []
        self.recommended_products = []
        self.recently_viewed_products = []
        self.quantity = element.TextBox(self, alias='Quantity Numeric Input', dom_id='id_quantity')
        self.add_to_cart = element.Button(self, alias='Add to Cart Button',
                                          css_selector='#add_to_basket_form button[type=submit]')
        self.ask = element.Link(self, alias='Ask a Question Link', css_selector='ul li:nth-child(1) > a')
        self.return_policy = element.Link(self, alias='Return Policy (See more...)',
                                          css_selector='ul li:nth-child(1) > a')
        self.write_review = element.Link(self, alias='Write Review Link', id_dom='write_review')
        self.add_to_wishlist = element.Button(self, alias='Love This (Wishlist) Button',
                                              css_selector='.product_main form.wishlist button[type=submit]')
        self.remove_from_wishlist = element.Button(self, alias='Remove from Wishlist Button',
                                                   css_selector='.product_main form.loved button[type=submit]')
        self.add_to_wishlist_guest = element.Button(self, alias='Love This (Wishlist) Button',
                                                    css_selector='.product_main button.wishlist')
        self.notify_me = element.Button(self, alias='Notify Me (On Stock) Button',
                                        css_selector='.product_main button[type=submit]')
        self.notify_email = element.TextBox(self, alias='Notify Me (On Stock) E-mail Textbox',
                                            name='email')
        self.share_fb = element.Link(self, alias='Share on FB Link', css_selector='.share > a.fb')
        self.share_pinterest = element.Link(self, alias='Share on Pinterest Link', css_selector='.share > a.pinterest')
        self.share_twitter = element.Link(self, alias='Share on Twitter Link', css_selector='.share > a.twitter')
        self.store_name = element.Link(self, alias='Store/ Partner Name Link', css_selector='h2.title > span > a')
        self.partner_mugshot = element.Image(self, alias='Partner Mugshot', css_selector='img.mugshot')
        self.partner_default_photo = element.Image(self, alias='Partner Default Photo', css_selector='img.no-mugshot')
        self.buy_other_items = element.Link(self, alias='Buy Other Items Link', css_selector='h2.title > span > a')
        self.details = element.NavigationTab(self, link_should_change=False, alias='Details Tab',
                                             css_selector='a.tab.details')
        self.reviews = element.NavigationTab(self, link_should_change=False, alias='Reviews Tab',
                                             css_selector='a.tab.reviews')
        self.extra_form_setup()

    def extra_form_setup(self):
        """Additional (one-time at least) form setup"""

        for x in range(5):
            x_plus_one = x + 1
            self.gallery_images.append(element.Image(self, alias='Gallery Image {}'.format(x_plus_one),
                                                     dom_id='gallery_image_{}'.format(x)))
            self.active_gallery_images.append(element.Image(self, alias='Active Gallery Image {}'.format(x_plus_one),
                                                            css_selector='.active #gallery_image_{}'.format(x)))
            self.gallery_thumbnail.append(element.ImageLink(
                self, alias='Gallery Thumbnail Image {}'.format(x_plus_one),
                css_selector='ol.thumbnail li:nth-of-type({}) img'.format(x_plus_one)))

        for key in ['GBP', 'USD', 'EUR', 'INR', 'IDR', 'PHP', 'THB', 'MYR']:
            self.converted_price[key] = element.Caption(self, alias='Price Converted ({})'.format(key),
                                                        css_selector='#currency_info.{}'.format(key.lower()))

    def update_controls(self):
        """Update controls for Catalogue Detail Page"""

        super(CatalogueDetailPage, self).update_controls()
        """
        self.other_products = self._update_control_group(container.PartnerOtherProducts)
        self.recommended_products = self._update_control_group(container.PartnerRecommendedProducts)
        self.recently_viewed_products = self._update_control_group(container.RecentlyViewedProducts)
        """


class PasswordResetPage(StandardPage):
    """Password Reset Page"""

    alias = 'Password Reset Confirmation Page'

    def form_setup(self):
        """Password Reset page controls"""

        super(PasswordResetPage, self).form_setup()
        self.logout = element.Link(self, alias='Logout Link from message', css_selector='p.logged-on > a')
        self.expired = element.Caption(self, alias='Expired Password Reset Link Message', css_selector='p.expired')
        self.password = element.TextBox(self, name='new_password1', alias='New Password Textbox')
        self.password_confirm = element.TextBox(self, name='new_password2', alias='New Password Confirm Textbox')
        self.reset_button = element.Button(self, css_selector='#password_reset_form button[type=submit]',
                                           alias='Reset Button')

    def set_password_key(self, key):
        """Convenience function to set password reset key onto url path

        :param str key: the password reset key
        """

        self.url_path = key

    def reset(self, password, password_confirm, link_should_change=True, timeout=None):
        """Input new password and submit

        :param str password: new account password
        :param str password_confirm: confirm new password
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        """

        self.password.input(password)
        self.password_confirm.input(password_confirm)
        self.reset_button.click(link_should_change=link_should_change, timeout=timeout)
