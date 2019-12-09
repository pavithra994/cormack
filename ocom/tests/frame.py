"""tests.frame.py - Frame classes for Page object model in Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from . import element, page, app


class Frame(element.Element, page.SeleniumPage):
    """Frame element/page"""

    item_type = 'Frame'

    # we need to do this to be able to call Selenium page's init
    def __init__(self, test_case, test_page, **kwargs):
        """Initialize Frame

        :param app.LiveServerTestCase test_case: reference to Test Case
        :param page.SeleniumPage test_page: reference to Test Page
        :param str css_selector: the frame's CSS selector
        :param str alias: the frame's alias
        """

        page.SeleniumPage.__init__(self, test_case, **kwargs)
        element.Element.__init__(self, test_page, **kwargs)
        self.page_alias = test_page.name
        self.form_setup()

    def form_setup(self):
        """Frame controls"""

        raise NotImplementedError("Add elements here")

    def switch(self, message='', update=True):
        """Switch to frame from page

        :param str message: the message to display
        :param bool update: if True, runs update reference first
        """

        if update:
            self._update_reference()

        self.utils.console("Switching to frame {} on {}...".format(self.alias, self.page_alias)
                           if message == '' else message)
        source = self._reference.get_attribute('src')

        if source:
            self.utils.console("Source url: {}".format(source), tabs=1)

        self.source.browser.switch_to.frame(self._reference)

    def unswitch(self, update=False):
        """Switch back to page from frame

        :param bool update: if True, runs update reference first
        """

        self.utils.console("Switching back from {} to {}...".format(self.alias, self.page_alias))
        self.source.browser.switch_to.default_content()

        # we do this afterwards
        if update:
            self._update_reference()

    def save_html(self, filename_without_path, message='', check_path=False, prettify=True):
        """Save html dump of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: The base filename without the absolute path
        :param str message: The message to display
        :param bool check_path: if True, check path with url property
        :param bool prettify: if True, prettifies html
        """

        super(Frame, self).save_html(
            filename_without_path,
            "Saving html of frame {}: {}".format(self.alias, filename_without_path) if message == '' else message,
            check_path, prettify)

    def save_screenshot(self, filename_without_path, message='', check_path=False, quality=60):
        """Save screenshot of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: filename, without path
        :param str message: The message to display
        :param bool check_path: if True, check path with url property
        :param int quality: If saving as JPEG, the compression quality (higher is better)
        """

        super(Frame, self).save_screenshot(
            filename_without_path, "Taking screenshot file of frame {}: {}".format(
                self.alias, filename_without_path) if message == '' else message,
            check_path, quality)


class CaptchaPopup(element.Popup, Frame):
    """Captcha Popup page"""

    alias = 'Captcha Popup'
    css_selector = 'body > div > div > iframe'

    # we need to do this to be able to call Selenium page's init
    def __init__(self, test_case, test_page, **kwargs):
        """CaptchaPopup initialize method

        :param app.LiveServerTestCase test_case: reference to Test Case
        :param page.SeleniumPage test_page: reference to Test Page
        :param str css_selector: the frame's CSS selector
        :param str alias: the frame's alias
        """

        page.SeleniumPage.__init__(self, test_case, **kwargs)
        element.Popup.__init__(self, test_page, **kwargs)
        self.page_alias = test_page.name
        self.form_setup()

    def form_setup(self):
        """Captcha Popup Frame controls"""

        pass


class CaptchaFrame(Frame):
    """Captcha Frame"""

    alias = 'Captcha Frame'
    css_selector = '#id_captcha iframe'

    def form_setup(self):
        """Captcha Frame controls"""

        self.not_a_robot = element.CheckBox(self, css_selector='.recaptcha-checkbox-checkmark',
                                            visible_css_selector='#recaptcha-anchor-label',
                                            alias="\'I Am not a Robot Checkbox",
                                            ignore_value=True)


class ZendeskHelpFrame(Frame):
    """Zendesk Frame"""

    alias = 'Zendesk Help Frame'
    css_selector = 'iframe#launcher'

    def form_setup(self):
        """Zendesk Frame controls"""

        self.help_label = element.Caption(self, css_selector='.src-component-Launcher-label', alias='Help Label')


class ZendeskFormFrame(Frame):
    """Zendesk Help Form Frame"""

    alias = 'Zendesk Form Frame'
    css_selector = 'iframe#ticketSubmissionForm'

    def form_setup(self):
        """Zendesk Frame controls"""

        self.cancel = element.Caption(self, css_selector='#Embed .ButtonGroup .c-btn', alias='Cancel Button (Box)')


class BraintreeFrame(Frame):
    """Braintree Payment Gateway Frame"""

    alias = 'Braintree Payment Gateway Frame'
    css_selector = '#braintree-dropin-frame'

    def form_setup(self):
        """Braintree Frame controls"""

        self.paypal = element.Button(self, dom_id='braintree-paypal-button', alias='Paypal Button')
        self.credit_card = element.TextBox(self, dom_id='credit-card-number', alias='Credit Card Number Textbox')
        self.expiration = element.TextBox(self, dom_id='expiration', alias='Expiry Date Textbox')


class FacebookShareButtonFrame(Frame):
    """Facebook Share Button Frame"""

    alias = 'Facebook Share Button Frame'
    css_selector = '.fb-share-button iframe'

    def form_setup(self):
        """Facebook Share Button Frame controls"""

        pass


class FacebookLikeShareButtonFrame(FacebookShareButtonFrame):
    """Facebook Like and Share Button Frame"""

    alias = 'Facebook Like and Share Button Frame'
    css_selector = '.fb-like iframe'
