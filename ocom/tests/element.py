"""tests.element.py - Element classes for Page object model in Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from . import wait, app


class Element(app.BaseItem):
    """Base HTML Element

    Except where noted: methods using self.reference should have an _update_reference run before it
    """

    item_type = 'Element'

    def _wait_for_page_to_load(self, timeout=None, expected_url_change=True, check_ready_state=False,
                               check_staleness=True, tabs=0):
        """Perform wait until page is detected as stale or url is changed

        :param float timeout: timeout to expire, in seconds
        :param bool expected_url_change: if True, expects for a link change to happen
        :param bool check_ready_state: if True, check for DOM ready state
        :param bool check_staleness: if True, check for page staleness
        :param int tabs: the number of tabs to prepend messages
        """

        tabs_plus_one = tabs + 1
        self.utils.start_timer('page_load', self.timers, tabs=tabs_plus_one)

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        if not self._is_reference_page_stale():
            self._wait_until_page_loaded(self, timeout, check_staleness=check_staleness,
                                         check_ready_state=check_ready_state)

        if expected_url_change:
            url_message = "Changes expected but url did not change: {}".format(self._page_url) \
                if self._page_url == self.source.browser.current_url \
                else "Change in url detected: {}".format(self.source.browser.current_url)
            self.utils.console(url_message, tabs=tabs_plus_one)
        elif self._is_reference_page_stale():
            self.utils.console("Page change detected.", tabs=tabs_plus_one)

        self._page_url = self.source.browser.current_url
        self.utils.time_elapsed('page_load', self.timers, tabs=tabs_plus_one)


class Image(Element):
    """Representing Image <img>"""

    @property
    def file_path(self):
        """Get image source path

        Note: this is the same as source_url property
        """

        return self.source_url


class Caption(Element):
    """Representing Caption/ Text element"""

    def click(self, message='', update=True):
        """Perform a click operation

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference(force=self.angular)

        self._perform_click(message, use_script=True)


class Label(Caption):
    """Representing <label> element"""

    @property
    def is_required(self):
        """Check if the required span tag is present inside the element

        :return: True if <span class="required"> is found
        """

        # we force a reference update since this is a property
        self._update_reference(inform=False)
        # below method may have an issue if html tag has spaces somewhere
        # return '<span class="required">' in self.reference.get_attribute('innerHTML')
        return self._reference_has_css_selector('span.required')


class Spinner(Caption):
    """Representing spinner element"""

    def wait_until_stale(self, message='', timeout=None, tabs=0, update=False, strict=True, post_timeout=2.0):
        # self._update_reference(force=self.angular)
        super(Spinner, self).wait_until_stale(message, timeout, tabs, update, strict)

        if post_timeout:
            self.utils.delay(post_timeout)


class Link(Element):
    """Representing <a> element"""

    def click(self, message='', timeout=None, update=True, new_tab=False, no_submit=False):
        """Perform a click operation

        :param str message: the message to display
        :param float timeout: the page timeout in seconds
        :param bool update: if True, runs update reference first
        :param bool new_tab: if True, opens link on a new tab/window handle
        :param bool no_submit: if True, no redirect is expected
        """

        if update:
            self._update_reference()

        self._page_url = self.source.browser.current_url
        # we call get_attribute directly so we won't have to call self._update_reference when update is false
        target_url = self._reference.get_attribute('data-url')
        href = self._reference.get_attribute('href')
        target = self._reference.get_attribute('target')

        self._perform_click(message)

        if target_url is None:
            if href:
                self.utils.console("Target url: {}".format(href), tabs=1)

            if isinstance(self.parent, app.BaseItem):
                self.parent.parent.target_url = None
            else:
                self.parent.target_url = None
        else:
            self.utils.console("Target url: {}".format(target_url), tabs=1)

            if isinstance(self.parent, app.BaseItem):
                self.parent.parent.target_url = target_url
            else:
                self.parent.target_url = target_url

        if new_tab or target == '_blank':
            self.utils.console("Opening page in new tab...")
        else:
            if no_submit:
                self.utils.console("No submit event should be triggered for {} click...".format(self.name), tabs=1)
            elif self.angular:
                self.utils.console("Click is angular in nature (page may change)...".format(self.name), tabs=1)
                if timeout:
                    self._wait_until_timeout(timeout)
            else:
                self._wait_for_page_to_load(timeout=timeout)


class ImageLink(Image, Link):
    """Representing clickable images"""

    def click(self, message='', timeout=None, update=True, new_tab=False, link_should_change=True, angular=False):
        """Perform a click operation

        :param str message: the message to display
        :param float timeout: the page timeout in seconds
        :param bool update: if True, runs update reference first
        :param bool new_tab: if True, opens link on a new tab/window handle
        :param bool link_should_change: if True, link should change so wait for page to load
        :param bool angular: if True, link is angular
        """

        if update:
            self._update_reference()

        self._perform_click(message, use_script=True)

        if new_tab:
            # TODO: perform some tab operations
            pass
        elif self.angular:
            self.utils.console("Click is angular in nature (page may change)...".format(self.name), tabs=1)
            if timeout:
                self._wait_until_timeout(timeout)

        elif link_should_change:
            self._wait_for_page_to_load(timeout=timeout)


class CaptionLink(Link, Caption):
    """Representing caption with a Link-style click"""

    def click(self, message='', timeout=None, update=True, new_tab=False, no_submit=False):
        """Perform a click operation

        :param str message: the message to display
        :param float timeout: the page timeout in seconds
        :param bool update: if True, runs update reference first
        :param bool new_tab: if True, opens link on a new tab/window handle
        :param bool no_submit: if True, no redirect is expected
        """

        if update:
            self._update_reference()

        self._perform_click(message, use_script=True)

        if new_tab:
            pass
        else:
            if no_submit:
                self.utils.console("No submit event should be triggered for {} click...".format(self.name), tabs=1)
            elif self.angular:
                self.utils.console("Click is angular in nature (page may change)...".format(self.name), tabs=1)
                if timeout:
                    self._wait_until_timeout(timeout)
            else:
                self._wait_for_page_to_load(timeout=timeout)


class TopMenuLink(Link):
    """Top Hover Menu Link"""

    pass


class SubMenuLink(Link):
    """Sub Menu Link"""

    pass


class LinkButton(Element):
    """Representing <a> element with button functions"""

    def click(self, message='', update=True):
        """Perform a click operation

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self._perform_click(message)


class Button(Link):
    """Representing <button> element"""

    def __init__(self, test_object, button_type='submit', **kwargs):
        """Button element initialization method

        :param tests.page.SeleniumPage or tests.container.Container test_object: the source test object
        :param str button_type: the button type to associate the element with (options: 'submit', 'button', 'clear')
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        super(Button, self).__init__(test_object, **kwargs)
        self.button_type = button_type

    def click(self, message='', link_should_change=True, timeout=None, no_submit=False, check_staleness=True,
              update=True):
        """Perform a click operation

        :param str message: the message to display
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        :param bool no_submit: if True and button type is 'submit', no DOM submit event is expected to be triggered
        :param bool check_staleness: if True check for staleness
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self._page_url = self.source.browser.current_url
        self._perform_click(message)

        if self.button_type == 'submit':
            if no_submit:
                self.utils.console("No submit event should be triggered for {} click...".format(self.name), tabs=1)
            elif self.angular:
                if link_should_change:
                    self.utils.console("Click is angular in nature (page should change)...".format(self.name), tabs=1)
                    self._wait_for_page_to_load(timeout=timeout, expected_url_change=True, check_staleness=False)
                else:
                    self.utils.console("Click is angular in nature...".format(self.name), tabs=1)
            else:
                self._wait_for_page_to_load(timeout=timeout, expected_url_change=link_should_change,
                                            check_staleness=check_staleness)
        elif self.button_type in ['button', 'clear']:
            self.utils.console("{} click should have triggered an event here (if any)...".format(self.name), tabs=1)

    def hover_and_click(self, pre_hover_element=None, message='', link_should_change=True, timeout=None,
                        no_submit=False, update=True, click_on_visible=True):
        """Hover over an element and click

        :param WebElement pre_hover_element: the element to hover on first if present
        :param str message: the message to display
        :param bool link_should_change: if True, it is expected that the url will change after click
        :param float timeout: the page timeout in seconds
        :param bool no_submit: if True and button type is submit, no DOM submit event was triggered
        :param bool update: if True, runs update reference first
        :param bool click_on_visible: if True, click when button is visible
        """

        if pre_hover_element is not None:
            pre_hover_element.hover(update=update)

            if click_on_visible:
                pre_hover_element.wait_until_visible()

        self.hover(update=update)

        if click_on_visible:
            self.wait_until_visible()

        self.click(message, link_should_change, timeout, no_submit, update)


class NavigationTab(Element):
    """Representing nav tab element"""

    def __init__(self, test_object, link_should_change=True, **kwargs):
        """Button element initialization method

        :param tests.page.SeleniumPage or tests.container.Container test_object: the source test object
        :param bool link_should_change: if True, link change is expected
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        super(NavigationTab, self).__init__(test_object, **kwargs)
        self.link_should_change = link_should_change

    def click(self, message='', timeout=None, update=True):
        """Perform a click operation

        :param str message: the message to display
        :param float timeout: the page timeout in seconds
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        if self.link_should_change:
            self._page_url = self.source.browser.current_url

        self._perform_click(message)

        if self.link_should_change:
            self._wait_for_page_to_load(timeout=timeout)


class InputElement(Element):
    """Representing general input elements <input>, <textarea>, <select>, etc..."""

    @property
    def is_required(self):
        """Check if input text has the required attribute"""

        # we force update reference since this is a property
        self._update_reference(inform=False)
        return self._reference.get_attribute('required') is not None

    def remove_required(self):
        """Remove required attribute from input"""

        if self.is_required:
            self.source.browser.execute_script(
                "document.querySelector('{}').required = false;".format(self.css_selector))

    def focus(self, update=True):
        """Focus on an element

        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.source.browser.execute_script("document.querySelector('{}').focus();".format(self.css_selector))

    def clear(self, update=True):
        """Remove any value from input

        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self._reference.clear()


class TextBox(InputElement):
    """Representing <input type=text> element"""

    def input(self, value, clear=True, focus=False, use_script=False, update=True):
        """Key in a value in the textbox

        :param str value: the value to enter
        :param bool clear: if True, clears current textbox input before entering any value
        :param bool focus: if True, runs a focus script on the element first
        :param bool use_script: if True, use a querySelector script on the element instead of selenium method
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Entering input for {}...".format(self.name))
        self.utils.console("Value: {}".format(value), tabs=1)

        if focus:
            self.focus(update=False)

        if clear:
            self.clear(update=False)

        if use_script:
            self.source.browser.execute_script("document.querySelector('{}').value = {};".format(
                self.css_selector, value))
        else:
            self._reference.send_keys(value)


class TextArea(TextBox):
    """Representing <textarea> element"""

    pass


class CheckBox(InputElement):
    """Representing <input type=checkbox> element"""

    def __init__(self, test_object, **kwargs):
        """
        :param tests.page.SeleniumPage or tests.container.Container test_object: the source test object
        :param str dom_id: the element DOM ID
        :param str name: the element DOM name
        :param str class_name: the element class name
        :param str css_selector: the element CSS selector
        :param str xpath: the element xpath
        :param str visible_css_selector: The CSS selector of the checkbox's label / visible element
        :param bool ignore_value: if True, ignore value checks when ticking/unticking checkbox
        """

        super(CheckBox, self).__init__(test_object, **kwargs)
        self._visible_css_selector = kwargs.get('visible_css_selector', '')
        self._ignore_value = kwargs.get('ignore_value', False)
        self._actual_css_selector = self.css_selector

    @property
    def is_checked(self):
        """Return checkbox toggle status

        :return: if checked, return True
        :rtype: bool
        """

        # we force a reference update since this is a property
        self._update_reference(inform=False)
        return self._checkbox_reference.is_selected()

    def _click_to_toggle(self):
        """Convenience function for alternating between actual checkbox clicks and checkbox label/other object clicks"""

        if self._visible_css_selector == '':
            self._reference.click()
        else:
            self.source.browser.execute_script("document.querySelector('{}').click();".format(
                self._visible_css_selector))

    def _update_reference(self, timeout=None, waiting=False, force=True, inform=True, strict=True, tabs=0):
        super(CheckBox, self)._update_reference(timeout, waiting, force, inform, strict, tabs)
        self._checkbox_reference = self._reference
        self._checkbox_description = self._description

        if self._visible_css_selector != '':
            self.css_selector = self._visible_css_selector
            super(CheckBox, self)._update_reference(timeout, waiting, force, inform, strict, tabs)
            self.css_selector = self._actual_css_selector

    def check(self, message='', update=True):
        """Tick on the checkbox

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        if message == '':
            message = "Ticking on {} with {}...".format(self.name, self._description) \
                if self._visible_css_selector == '' \
                else "Ticking on {} with label {}...".format(self.name, self._description)

        self.utils.console(message)

        if self._ignore_value:
            self._click_to_toggle()
        else:
            if self._checkbox_reference.is_selected():
                self.utils.console("{} already ticked.".format(self.name), tabs=1)
            else:
                self._click_to_toggle()

    def uncheck(self, message='', update=True):
        """Untick on the checkbox

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        if message == '':
            message = "Unticking on {} with {}...".format(self.name, self._description) \
                if self._visible_css_selector == '' \
                else "Unticking on {} with label {}...".format(self.name, self._description)

        self.utils.console(message)

        if self._ignore_value:
            self._click_to_toggle()
        else:
            if self._checkbox_reference.is_selected():
                self._click_to_toggle()
            else:
                self.utils.console("{} already unticked.".format(self.name), tabs=1)


class RadioButton(InputElement):
    """Representing <input type=radio> element"""

    def __init__(self, test_object, **kwargs):
        """
        :param tests.page.SeleniumPage or tests.container.Container test_object: the source test object
        :param str dom_id: the element DOM ID
        :param str name: the element DOM name
        :param str class_name: the element class name
        :param str css_selector: the element CSS selector
        :param str xpath: the element xpath
        :param bool ignore_value: if True, ignore value checks when ticking/unticking checkbox
        """

        super(RadioButton, self).__init__(test_object, **kwargs)
        self._ignore_value = kwargs.get('ignore_value', False)
        self._actual_css_selector = self.css_selector

    @property
    def is_selected(self):
        """Return radio button toggle status

        :return: if selected, return True
        :rtype: bool
        """

        # we force a reference update since this is a property
        self._update_reference(inform=False)
        return self._reference.is_selected()

    def select(self, message='', update=True):
        """Select on the radio button

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Selecting {} with {}...".format(self.name, self._description) if message == '' else message)

        if self._ignore_value:
            self._reference.click()
        else:
            if self._reference.is_selected():
                self.utils.console("{} already selected.".format(self.name), tabs=1)
            else:
                self._reference.click()


class Popup(Element):
    """Special element for popup/dialogs"""

    def send_escape_key(self, message='', update=True):
        """Attempt to close a popup by sending an escape key to it

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Sending escape key on {} with {}...".format(self.name, self._description)
                           if message == '' else message)
        self._send_escape_key()


class DropDown(InputElement):
    """Representing <select> element"""

    def select(self, value, update=True):
        """Click or select the value from available options

        :param str value: the new value of the dropdown
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Selecting option for {}...".format(self.name))
        self.utils.console("Value: {}".format(value), tabs=1)
        self.source.browser.execute_script("document.querySelector('{}').value = '{}';".format(
            self.css_selector, value))
        self.source.browser.execute_script("$('{}').trigger('change');".format(self.css_selector))

    def select_text(self, text, update=True):
        """Click or select the dropdown based on option text

        :param str text: the option with the dropdown text to select
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        script = "$('{} option').filter(function() {{ return $(this).text() == {}; }}).prop('selected', true);".\
            format(self.css_selector, self.utils.escape_string(text))
        self.utils.console("Selecting option for {}...".format(self.name))
        self.utils.console("Text: {}".format(text), tabs=1)
        self.source.browser.execute_script(script)
        self.source.browser.execute_script("$('{}').trigger('change');".format(self.css_selector))


class SelectListBox(DropDown):
    """Representing <select> element"""
    pass
