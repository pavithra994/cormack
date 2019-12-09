"""tests.live.test_account_access.py - Account Access Tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.test import override_settings
from ocom.tests import app
from tests import fixtures, page


@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher', ))
class AccountAccessTest(app.OcomLiveServerTestCaseNoFixtures):
    heading = "---Account Access test---"
    always_reset_browser = False

    @classmethod
    def setUpClass(cls):
        cls.factory = fixtures.Sampler()
        super(AccountAccessTest, cls).setUpClass()

    def setUp(self):
        super(AccountAccessTest, self).setUp()
        self.homepage = page.HomePage(self)
        self.login_page = page.SigninPage(self)
        self.landing_page = page.LandingPage(self)

    def test_login_and_logout(self):
        # region pre-test routines
        user = self.factory.user(password=self.common_password)
        # endregion

        # region test: check page access
        self.homepage.navigate(skip=True)
        # self.homepage.redirect()
        self.assertions.assert_element_present([
            self.homepage.logo,
        ])
        self.homepage.save_screenshot('homepage_start.jpg')
        self.homepage.save_html('homepage_start.html')
        self.utils.delay(4)
        self.login_page.redirect()
        self.login_page.save_screenshot('signin_page_start.jpg')
        self.login_page.save_html('signin_page_start.html')

        self.assertions.assert_element_present([
            self.login_page.identification,
            self.login_page.password,
            self.login_page.submit,
        ])

        # click without entering anything
        self.login_page.submit.click(link_should_change=False)
        self.assertions.assert_element_present([
            self.login_page.error,
            self.login_page.submit,
        ])

        # click by entering wrong credentials
        self.login_page.identification.input('test')
        self.login_page.password.input('testing')
        self.login_page.submit.click(link_should_change=False)
        self.assertions.assert_element_present([
            self.login_page.error,
            self.login_page.submit,
        ])
        self.login_page.save_screenshot('signin_page_wrong_credentials.jpg')

        # click by entering right credentials
        self.login_page.identification.input(user.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.site,
            self.landing_page.top_nav_menu.account_dropdown,
            self.landing_page.job_menu.list,
            self.landing_page.job_menu.new,
        ])
        self.landing_page.save_screenshot('landing_page_start.jpg')
        self.landing_page.save_html('landing_page_start.html')

        # logout
        self.landing_page.top_nav_menu.account_dropdown.click(timeout=1)
        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.account_profile,
            self.landing_page.top_nav_menu.logout,
        ])

        self.landing_page.top_nav_menu.logout.click(timeout=1)
        self.login_page.redirect()
        self.assertions.assert_element_present([
            self.login_page.success,
            self.login_page.submit,
        ])
        self.login_page.save_screenshot('signin_page_after_logout.jpg')
        self.login_page.save_html('signin_page_after_logout.html')

    def test_landing_page(self):
        # region pre-test routines
        user = self.factory.user(password=self.common_password)
        user_with_role = self.factory.user(password=self.common_password)
        superuser = self.factory.admin_user(password=self.common_password)
        # endregion

        # region login as user with no roles
        self.login_page.navigate()
        self.login_page.identification.input(user.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.landing_page.top_nav_menu.account_dropdown.click(timeout=1)
        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.account_profile,
            self.landing_page.top_nav_menu.logout,
        ])

        self.assertions.assert_element_not_present([
            self.landing_page.top_nav_menu.admin_dashboard,
        ])
        self.landing_page.save_screenshot('landing_page_user_no_role.jpg')
        self.landing_page.top_nav_menu.logout.click(timeout=1)
        self.login_page.redirect()
        # endregion

        # region login as user with roles
        self.login_page.identification.input(user_with_role.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.site,
            self.landing_page.top_nav_menu.account_dropdown,
            self.landing_page.job_menu.list,
            self.landing_page.job_menu.new,
        ])

        self.landing_page.top_nav_menu.account_dropdown.click(timeout=1, no_submit=True)
        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.account_profile,
            self.landing_page.top_nav_menu.logout,
        ])
        self.assertions.assert_element_not_present([
            self.landing_page.top_nav_menu.admin_dashboard,
        ])
        self.landing_page.save_screenshot('landing_page_user_with_role.jpg')
        self.landing_page.top_nav_menu.logout.click(timeout=1)
        self.login_page.redirect()
        # endregion

        # region login as super user
        self.login_page.identification.input(superuser.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.site,
            self.landing_page.top_nav_menu.account_dropdown,
            self.landing_page.job_menu.list,
            self.landing_page.job_menu.new,
        ])

        self.landing_page.top_nav_menu.account_dropdown.click(timeout=1)
        self.assertions.assert_element_present([
            self.landing_page.top_nav_menu.admin_dashboard,
            self.landing_page.top_nav_menu.account_profile,
            self.landing_page.top_nav_menu.logout,
        ])
        self.landing_page.save_screenshot('landing_page_superuser.jpg')
        self.landing_page.top_nav_menu.logout.click(timeout=1)
        self.login_page.redirect()
        # endregion
