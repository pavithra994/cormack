"""tests.live.test_admin_access.py - Live Admin Page Tests"""

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
class AdminDashboardTest(app.OcomLiveServerTestCaseNoFixtures):
    heading = "---Admin Dashboard Pages test---"
    always_reset_browser = False

    @classmethod
    def setUpClass(cls):
        cls.factory = fixtures.Sampler()
        super(AdminDashboardTest, cls).setUpClass()

    def setUp(self):
        super(AdminDashboardTest, self).setUp()
        self.dashboard_page = page.AdminPage(self)
        self.admin_login_page = page.AdminSigninPage(self)
        self.admin_logout_page = page.AdminSignoutPage(self)
        self.admin_client_list_page = page.AdminClientListPage(self)
        self.admin_client_add_page = page.AdminClientAddPage(self)
        self.admin_client_edit_page = page.AdminClientEditPage(self)
        self.admin_subbie_list_page = page.AdminSubbieListPage(self)
        self.admin_subbie_add_page = page.AdminSubbieAddPage(self)
        self.admin_subbie_edit_page = page.AdminSubbieEditPage(self)
        self.admin_supervisor_list_page = page.AdminSupervisorListPage(self)
        self.admin_supervisor_add_page = page.AdminSupervisorAddPage(self)
        self.admin_supervisor_edit_page = page.AdminSupervisorEditPage(self)
        self.user = self.factory.user(password=self.common_password)
        self.superuser = self.factory.admin_user(password=self.common_password)

    def test_dashbboard_page(self):
        # region pre-test routines
        self.utils.start_timer('dashboard', self.timers, "Checking Dashboard index page...")
        # endregion

        # region test: check page access
        self.dashboard_page.navigate(skip=True)
        self.admin_login_page.redirect()
        self.admin_login_page.save_screenshot('admin_login_page_start.jpg')
        self.admin_login_page.save_html('admin_login_page_start.html')

        self.assertions.assert_element_present([
            self.admin_login_page.identification,
            self.admin_login_page.password,
            self.admin_login_page.submit,
            self.admin_login_page.footer.ocomsoft_link,
            self.admin_login_page.footer.footer_title,
            self.admin_login_page.footer.version,
        ])

        self.assertions.assert_element_not_present([
            self.admin_login_page.top_nav_menu.change_password,
            self.admin_login_page.error
        ])

        # click without entering anything
        self.admin_login_page.submit.click(no_submit=True)
        self.assertions.assert_element_present(self.admin_login_page.submit)

        # click by entering wrong credentials
        self.admin_login_page.identification.input('test')
        self.admin_login_page.password.input('testing')
        self.admin_login_page.submit.click()
        self.admin_login_page.redirect_back()
        self.assertions.assert_element_present([
            self.admin_login_page.submit,
            self.admin_login_page.error
        ])
        self.admin_login_page.save_screenshot('admin_signin_page_error_wrong_credentials.jpg')
        # endregion

        # click by entering ordinary account
        self.admin_login_page.identification.input(self.user.username)
        self.admin_login_page.password.input(self.common_password)
        self.admin_login_page.submit.click()
        self.admin_login_page.redirect_back()
        self.assertions.assert_element_present([
            self.admin_login_page.submit,
            self.admin_login_page.error
        ])
        self.admin_login_page.save_screenshot('admin_signin_page_error_ordinary_account.jpg')
        # endregion

        # click by entering superuser account
        self.admin_login_page.identification.input(self.superuser.username)
        self.admin_login_page.password.input(self.common_password)
        self.admin_login_page.submit.click()
        self.dashboard_page.redirect()

        self.assertions.assert_element_present([
            self.dashboard_page.modules.clients.title,
            self.dashboard_page.modules.subbies.add,
            self.dashboard_page.modules.supervisors.change,
            self.dashboard_page.code_tables.drain_types.add,
            self.dashboard_page.code_tables.depot_types.add,
            self.dashboard_page.code_tables.file_types.change,
            self.dashboard_page.code_tables.job_types.add,
            self.dashboard_page.code_tables.paving_colours.title,
            self.dashboard_page.code_tables.paving_types.change,
            self.dashboard_page.code_tables.repair_types.add,
            self.dashboard_page.code_tables.subbie_types.title,
            self.dashboard_page.code_tables.task_types.change,
            self.dashboard_page.authentication.roles.change,
            self.dashboard_page.footer.ocomsoft_link,
            self.dashboard_page.footer.footer_title,
            self.dashboard_page.footer.version,
            self.admin_login_page.top_nav_menu.change_password,
            self.admin_login_page.top_nav_menu.logout,
        ])

        self.assertions.assert_element_not_present([
            self.dashboard_page.error
        ])

        self.dashboard_page.save_screenshot('admin_dashboard_page_start.jpg')

        # click on logout link
        self.dashboard_page.top_nav_menu.logout.click()
        self.admin_logout_page.redirect()

        self.assertions.assert_element_present([
            self.admin_logout_page.message,
            self.admin_logout_page.footer.ocomsoft_link,
            self.admin_logout_page.footer.footer_title,
            self.admin_logout_page.footer.version,
            self.admin_logout_page.left_sidebar.login,
            self.admin_logout_page.left_sidebar.main,
            self.admin_logout_page.top_nav_menu.site
        ])

        self.assertions.assert_element_not_present([
            self.admin_logout_page.top_nav_menu.change_password,
            self.admin_logout_page.top_nav_menu.logout,
            self.admin_logout_page.error
        ])

        self.dashboard_page.save_screenshot('admin_signout_page_start.jpg')

        # click on login link
        self.admin_logout_page.left_sidebar.login.click()
        self.admin_login_page.redirect()
        self.assertions.assert_element_present([
            self.admin_login_page.submit,
        ])

        self.assertions.assert_element_not_present([
            self.admin_login_page.left_sidebar.login,
            self.admin_login_page.error
        ])
        # endregion

        self.utils.time_elapsed('dashboard', self.timers)

    def test_client_page(self):
        # region pre-test routines
        self.utils.start_timer('client', self.timers, "Checking Clients Admin page...")
        supplier_type = self.factory.subbie_type(code='supplier')
        self.factory.subbie_type(code='employee')
        self.factory.subbie_type(code='subbie')
        supplier = self.factory.subbie(name='Test Subbie', type=supplier_type)
        # endregion

        # region test: check page access
        self.dashboard_page.navigate(skip=True)
        self.admin_login_page.redirect()
        self.admin_login_page.identification.input(self.superuser.username)
        self.admin_login_page.password.input(self.common_password)
        self.admin_login_page.submit.click()
        self.dashboard_page.redirect()
        self.dashboard_page.modules.clients.change.click()
        self.admin_client_list_page.redirect()
        self.admin_client_list_page.save_screenshot('admin_client_list_page_start.jpg')
        self.admin_client_list_page.save_html('admin_client_list_page_start.html')
        #   Note: unable to search active_status dropdown because name is not yet populated
        self.assertions.assert_element_present([
            self.admin_client_list_page.keyword,
            # self.admin_client_list_page.active_status,
            # self.admin_client_list_page.active_start_date,
            # self.admin_client_list_page.active_end_date,
            self.admin_client_list_page.search,
            self.admin_client_list_page.add,
        ])
        self.assertions.assert_element_not_present([
            self.admin_client_list_page.client_name,
            self.admin_client_list_page.xero_customer,
            self.admin_client_list_page.send_invoices,
            self.admin_client_list_page.part_a_required,
            self.admin_client_list_page.they_supply_pump,
            self.admin_client_list_page.active_start_date,
            self.admin_client_list_page.active_end_date,
        ])
        # endregion

        # region test: check add page access
        self.admin_client_list_page.add.click()
        self.admin_client_add_page.redirect()

        self.assertions.assert_element_present([
            self.admin_client_add_page.save,
            self.admin_client_add_page.save_and_continue,
            self.admin_client_add_page.save_add_another,
            self.admin_client_add_page.client_name,
            self.admin_client_add_page.xero_customer,
            self.admin_client_add_page.suppliers,
            self.admin_client_add_page.send_invoices,
            self.admin_client_add_page.part_a_required,
            self.admin_client_add_page.they_supply_pump,
            self.admin_client_add_page.active_start_date,
            self.admin_client_add_page.active_end_date,
        ])
        self.admin_client_add_page.save_screenshot('admin_client_add_page_start.jpg')
        self.admin_client_add_page.save_html('admin_client_add_page_start.html')
        # endregion

        # region test: check add page restrictions
        self.admin_client_add_page.save.click()
        self.admin_client_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_client_add_page.error,
            self.admin_client_add_page.client_name,
            self.admin_client_add_page.xero_customer,
            self.admin_client_add_page.suppliers,
            self.admin_client_add_page.send_invoices,
            self.admin_client_add_page.part_a_required,
            self.admin_client_add_page.they_supply_pump,
            self.admin_client_add_page.active_start_date,
            self.admin_client_add_page.active_end_date,
        ])

        self.admin_client_add_page.save_screenshot('admin_client_add_page_add_empty.jpg')
        self.admin_client_add_page.save_html('admin_client_add_page_add_empty.html')
        # endregion

        # region test: client page data entry, save and edit
        client_name = "Test Customer 1"
        self.admin_client_add_page.client_name.input(client_name)
        # self.admin_client_add_page.xero_customer.input("TEST001")
        self.admin_client_add_page.suppliers.select_text(supplier.name)
        self.admin_client_add_page.send_invoices.uncheck()
        self.admin_client_add_page.part_a_required.uncheck()
        self.admin_client_add_page.they_supply_pump.check()
        self.admin_client_add_page.save_and_continue.click()
        self.admin_client_edit_page.redirect(absorb_url=True)

        self.assertions.assert_element_present([
            self.admin_client_edit_page.success,
            self.admin_client_edit_page.client_name,
            self.admin_client_edit_page.xero_customer,
            self.admin_client_edit_page.suppliers,
            self.admin_client_edit_page.tools.add,
        ])
        self.assertions.assert_element_value(self.admin_client_edit_page.client_name, client_name)
        self.admin_client_edit_page.save_screenshot('admin_client_add_page_saved_continue.jpg')
        # endregion

        # region test: client page data entry, save only
        self.admin_client_edit_page.tools.add.click()
        self.admin_client_add_page.redirect()
        client_name = "Test Customer 2"
        self.admin_client_add_page.client_name.input(client_name)
        # self.admin_client_add_page.xero_customer.input("TEST002")
        self.admin_client_add_page.suppliers.select_text(supplier.name)
        self.admin_client_add_page.save.click()
        self.admin_client_list_page.redirect()

        self.assertions.assert_element_present([
            self.admin_client_list_page.success,
            self.admin_client_list_page.client_name,
            self.admin_client_list_page.xero_customer,
            self.admin_client_list_page.part_a_required,
            self.admin_client_list_page.they_supply_pump,
            self.admin_client_list_page.active_start_date,
            self.admin_client_list_page.active_end_date,
            self.admin_client_list_page.clients[0].client_name,
            self.admin_client_list_page.clients[1].xero_customer,
        ])
        self.admin_client_list_page.save_screenshot('admin_client_add_page_saved.jpg')
        # endregion

        # region test: client page data entry, save and add
        self.admin_client_list_page.add.click()
        self.admin_client_add_page.redirect()
        client_name = "Test Customer 3"
        self.admin_client_add_page.client_name.input(client_name)
        # self.admin_client_add_page.xero_customer.input("TEST003")
        self.admin_client_add_page.suppliers.select_text(supplier.name)
        self.admin_client_add_page.save_add_another.click()
        self.admin_client_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_client_add_page.success,
            self.admin_client_add_page.client_name,
            self.admin_client_add_page.xero_customer,
            self.admin_client_add_page.part_a_required,
            self.admin_client_add_page.they_supply_pump,
            self.admin_client_add_page.active_start_date,
            self.admin_client_add_page.active_end_date,
        ])
        self.assertions.assert_element_value(self.admin_client_add_page.client_name, "")
        self.admin_client_add_page.save_screenshot('admin_client_add_page_save_and_add.jpg')
        # endregion

        self.utils.time_elapsed('client', self.timers)

    def test_subbie_page(self):
        # region pre-test routines
        self.utils.start_timer('subbie', self.timers, "Checking Subbie Admin page...")
        supplier_type = self.factory.subbie_type(code='supplier')
        employee_type = self.factory.subbie_type(code='employee')
        sub_subbie = self.factory.subbie_type(code='subbie')
        # endregion

        # region test: check page access
        self.dashboard_page.navigate(skip=True)
        self.admin_login_page.redirect()
        self.admin_login_page.identification.input(self.superuser.username)
        self.admin_login_page.password.input(self.common_password)
        self.admin_login_page.submit.click()
        self.dashboard_page.redirect()
        self.dashboard_page.modules.subbies.change.click()
        self.admin_subbie_list_page.redirect()
        self.admin_subbie_list_page.save_screenshot('admin_subbie_list_page_start.jpg')
        self.admin_subbie_list_page.save_html('admin_subbie_list_page_start.html')
        #   Note: unable to search active_status dropdown because name is not yet populated
        self.assertions.assert_element_present([
            self.admin_subbie_list_page.keyword,
            # self.admin_subbie_list_page.active_status,
            # self.admin_subbie_list_page.active_start_date,
            # self.admin_subbie_list_page.active_end_date,
            self.admin_subbie_list_page.search,
            self.admin_subbie_list_page.add,
        ])
        self.assertions.assert_element_not_present([
            self.admin_subbie_list_page.subbie_name,
            self.admin_subbie_list_page.type,
            self.admin_subbie_list_page.username,
            self.admin_subbie_list_page.email,
            self.admin_subbie_list_page.active_start_date,
            self.admin_subbie_list_page.active_end_date,
        ])
        # endregion

        # region test: check add page access
        self.admin_subbie_list_page.add.click()
        self.admin_subbie_add_page.redirect()

        self.assertions.assert_element_present([
            self.admin_subbie_add_page.save,
            self.admin_subbie_add_page.save_and_continue,
            self.admin_subbie_add_page.save_add_another,
            self.admin_subbie_add_page.subbie_name,
            self.admin_subbie_add_page.type,
            self.admin_subbie_add_page.xero_supplier,
            self.admin_subbie_add_page.rate_per_meter,
            self.admin_subbie_add_page.jobs_per_day,
            self.admin_subbie_add_page.can_see_plans_before_accept,
            self.admin_subbie_add_page.username,
            self.admin_subbie_add_page.password,
            self.admin_subbie_add_page.email,
            self.admin_subbie_add_page.enabled,
            self.admin_subbie_add_page.active_start_date,
            self.admin_subbie_add_page.active_end_date,
        ])
        self.admin_subbie_add_page.save_screenshot('admin_subbie_add_page_start.jpg')
        self.admin_subbie_add_page.save_html('admin_subbie_add_page_start.html')
        # endregion

        # region test: check add page restrictions
        self.admin_subbie_add_page.save.click()
        self.admin_subbie_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_subbie_add_page.error,
            self.admin_subbie_add_page.subbie_name,
            self.admin_subbie_add_page.type,
            self.admin_subbie_add_page.rate_per_meter,
            self.admin_subbie_add_page.jobs_per_day,
            self.admin_subbie_add_page.can_see_plans_before_accept,
            self.admin_subbie_add_page.username,
            self.admin_subbie_add_page.password,
            self.admin_subbie_add_page.email,
            self.admin_subbie_add_page.enabled,
            self.admin_subbie_add_page.active_start_date,
            self.admin_subbie_add_page.active_end_date,
        ])

        self.admin_subbie_add_page.save_screenshot('admin_subbie_add_page_add_empty.jpg')
        self.admin_subbie_add_page.save_html('admin_subbie_add_page_add_empty.html')
        # endregion

        # region test: subbie page data entry, save and edit
        subbie_name = "Test Subbie 1"
        self.admin_subbie_add_page.subbie_name.input(subbie_name)
        self.admin_subbie_add_page.type.select_text(supplier_type.description)
        # self.admin_subbie_add_page.xero_supplier.input("TEST001")
        self.admin_subbie_add_page.rate_per_meter.input('1.01')
        self.admin_subbie_add_page.jobs_per_day.input('2')
        self.admin_subbie_add_page.can_see_plans_before_accept.check()
        self.admin_subbie_add_page.account_collapser.click(no_submit=True)
        self.admin_subbie_add_page.username.input('test001')
        self.admin_subbie_add_page.password.input('test001')
        self.admin_subbie_add_page.confirm_password.input('test001')
        self.admin_subbie_add_page.email.input('test001@testing.org')
        self.admin_subbie_add_page.enabled.check()
        self.admin_subbie_add_page.save_and_continue.click()
        self.admin_subbie_edit_page.redirect(absorb_url=True)

        self.assertions.assert_element_present([
            self.admin_subbie_edit_page.success,
            self.admin_subbie_edit_page.subbie_name,
            self.admin_subbie_edit_page.type,
            self.admin_subbie_edit_page.xero_supplier,
            self.admin_subbie_edit_page.tools.add,
        ])
        self.assertions.assert_element_value(self.admin_subbie_edit_page.subbie_name, subbie_name)
        self.admin_subbie_edit_page.save_screenshot('admin_subbie_add_page_saved_continue.jpg')
        # endregion

        # region test: client page data entry, save only
        self.admin_subbie_edit_page.tools.add.click()
        self.admin_subbie_add_page.redirect()
        subbie_name = "Test Subbie 2"
        self.admin_subbie_add_page.subbie_name.input(subbie_name)
        # self.admin_subbie_add_page.xero_supplier.input("TEST002")
        self.admin_subbie_add_page.type.select_text(employee_type.description)
        # TODO: check why username password empty allowed
        self.admin_subbie_add_page.save.click()
        self.admin_subbie_list_page.redirect()

        self.assertions.assert_element_present([
            self.admin_subbie_list_page.success,
            self.admin_subbie_list_page.subbie_name,
            self.admin_subbie_list_page.type,
            self.admin_subbie_list_page.username,
            self.admin_subbie_list_page.email,
            self.admin_subbie_list_page.active_start_date,
            self.admin_subbie_list_page.active_end_date,
            self.admin_subbie_list_page.subbies[0].subbie_name,
            self.admin_subbie_list_page.subbies[1].type,
        ])
        self.admin_subbie_list_page.save_screenshot('admin_subbie_add_page_saved.jpg')
        # endregion

        # region test: subbie page data entry, save and add
        self.admin_subbie_list_page.add.click()
        self.admin_subbie_add_page.redirect()
        subbie_name = "Test Subbie 3"
        self.admin_subbie_add_page.subbie_name.input(subbie_name)
        # self.admin_subbie_add_page.xero_supplier.input("TEST003")
        self.admin_subbie_add_page.type.select_text(sub_subbie.description)
        self.admin_subbie_add_page.save_add_another.click()
        self.admin_subbie_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_subbie_add_page.success,
            self.admin_subbie_add_page.subbie_name,
            self.admin_subbie_add_page.xero_supplier,
            self.admin_subbie_add_page.type,
            self.admin_subbie_add_page.rate_per_meter,
            self.admin_subbie_add_page.jobs_per_day,
            self.admin_subbie_add_page.can_see_plans_before_accept,
            self.admin_subbie_add_page.username,
            self.admin_subbie_add_page.password,
            self.admin_subbie_add_page.email,
            self.admin_subbie_add_page.enabled,
            self.admin_subbie_add_page.active_start_date,
            self.admin_subbie_add_page.active_end_date,
        ])
        self.assertions.assert_element_value(self.admin_subbie_add_page.subbie_name, "")
        self.admin_subbie_add_page.save_screenshot('admin_subbie_add_page_save_and_add.jpg')
        # endregion

        self.utils.time_elapsed('subbie', self.timers)

    def test_supervisor_page(self):
        # region pre-test routines
        self.utils.start_timer('supervisor', self.timers, "Checking Supervisor Admin page...")
        # endregion

        # region test: check page access
        self.dashboard_page.navigate(skip=True)
        self.admin_login_page.redirect()
        self.admin_login_page.identification.input(self.superuser.username)
        self.admin_login_page.password.input(self.common_password)
        self.admin_login_page.submit.click()
        self.dashboard_page.redirect()
        self.dashboard_page.modules.supervisors.change.click()
        self.admin_supervisor_list_page.redirect()
        self.admin_supervisor_list_page.save_screenshot('admin_supervisor_list_page_start.jpg')
        self.admin_supervisor_list_page.save_html('admin_supervisor_list_page_start.html')
        #   Note: unable to search active_status dropdown because name is not yet populated
        self.assertions.assert_element_present([
            self.admin_supervisor_list_page.keyword,
            # self.admin_supervisor_list_page.active_status,
            # self.admin_supervisor_list_page.active_start_date,
            # self.admin_supervisor_list_page.active_end_date,
            self.admin_supervisor_list_page.search,
            self.admin_supervisor_list_page.add,
        ])
        self.assertions.assert_element_not_present([
            self.admin_supervisor_list_page.supervisor_name,
            self.admin_supervisor_list_page.username,
            self.admin_supervisor_list_page.email,
            self.admin_supervisor_list_page.active_start_date,
            self.admin_supervisor_list_page.active_end_date,
        ])
        # endregion

        # region test: check add page access
        self.admin_supervisor_list_page.add.click()
        self.admin_supervisor_add_page.redirect()

        self.assertions.assert_element_present([
            self.admin_supervisor_add_page.save,
            self.admin_supervisor_add_page.save_and_continue,
            self.admin_supervisor_add_page.save_add_another,
            self.admin_supervisor_add_page.supervisor_name,
            self.admin_supervisor_add_page.username,
            self.admin_supervisor_add_page.password,
            self.admin_supervisor_add_page.email,
            self.admin_supervisor_add_page.phone_number,
            self.admin_supervisor_add_page.enabled,
            self.admin_supervisor_add_page.active_start_date,
            self.admin_supervisor_add_page.active_end_date,
        ])
        self.admin_supervisor_add_page.save_screenshot('admin_supervisor_add_page_start.jpg')
        self.admin_supervisor_add_page.save_html('admin_supervisor_add_page_start.html')
        # endregion

        # region test: check add page restrictions
        self.admin_supervisor_add_page.save.click()
        self.admin_supervisor_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_supervisor_add_page.error,
            self.admin_supervisor_add_page.supervisor_name,
            self.admin_supervisor_add_page.username,
            self.admin_supervisor_add_page.password,
            self.admin_supervisor_add_page.email,
            self.admin_supervisor_add_page.phone_number,
            self.admin_supervisor_add_page.enabled,
            self.admin_supervisor_add_page.active_start_date,
            self.admin_supervisor_add_page.active_end_date,
        ])

        self.admin_supervisor_add_page.save_screenshot('admin_supervisor_add_page_empty.jpg')
        self.admin_supervisor_add_page.save_html('admin_supervisor_add_page_empty.html')
        # endregion

        # region test: supervisor page data entry, save and edit
        supervisor_name = "Test Supervisor 1"
        self.admin_supervisor_add_page.supervisor_name.input(supervisor_name)
        # self.admin_supervisor_add_page.account_collapser.click(no_submit=True)
        self.admin_supervisor_add_page.username.input('test001')
        self.admin_supervisor_add_page.password.input('test001')
        self.admin_supervisor_add_page.confirm_password.input('test001')
        self.admin_supervisor_add_page.email.input('test001@testing.org')
        self.admin_supervisor_add_page.phone_number.input('632001234459')
        self.admin_supervisor_add_page.enabled.check()
        self.admin_supervisor_add_page.save_and_continue.click()
        self.admin_supervisor_edit_page.redirect(absorb_url=True)

        self.assertions.assert_element_present([
            self.admin_supervisor_edit_page.success,
            self.admin_supervisor_edit_page.supervisor_name,
            self.admin_supervisor_edit_page.tools.add,
        ])
        self.assertions.assert_element_value(self.admin_supervisor_edit_page.supervisor_name, supervisor_name)
        self.admin_supervisor_edit_page.save_screenshot('admin_supervisor_add_page_saved_continue.jpg')
        # endregion

        # region test: client page data entry, save only
        self.admin_supervisor_edit_page.tools.add.click()
        self.admin_supervisor_add_page.redirect()
        supervisor_name = "Test Supervisor 2"
        self.admin_supervisor_add_page.supervisor_name.input(supervisor_name)
        self.admin_supervisor_add_page.account_collapser.click(no_submit=True)
        self.admin_supervisor_add_page.username.input('test002')
        self.admin_supervisor_add_page.password.input('test002')
        self.admin_supervisor_add_page.confirm_password.input('test002')
        self.admin_supervisor_add_page.save.click()
        self.admin_supervisor_list_page.redirect()

        self.assertions.assert_element_present([
            self.admin_supervisor_list_page.success,
            self.admin_supervisor_list_page.supervisor_name,
            self.admin_supervisor_list_page.username,
            self.admin_supervisor_list_page.email,
            self.admin_supervisor_list_page.active_start_date,
            self.admin_supervisor_list_page.active_end_date,
            self.admin_supervisor_list_page.supervisors[0].supervisor_name,
            self.admin_supervisor_list_page.supervisors[1].username,
        ])
        self.admin_supervisor_list_page.save_screenshot('admin_supervisor_add_page_saved.jpg')
        # endregion

        # region test: supervisor page data entry, save and add
        self.admin_supervisor_list_page.add.click()
        self.admin_supervisor_add_page.redirect()
        supervisor_name = "Test Supervisor 3"
        self.admin_supervisor_add_page.supervisor_name.input(supervisor_name)
        self.admin_supervisor_add_page.save_add_another.click()
        self.admin_supervisor_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_supervisor_add_page.error,
            self.admin_supervisor_add_page.supervisor_name,
            self.admin_supervisor_add_page.username,
            self.admin_supervisor_add_page.email,
            self.admin_supervisor_add_page.active_start_date,
            self.admin_supervisor_add_page.active_end_date,
        ])
        self.assertions.assert_element_value(self.admin_supervisor_add_page.supervisor_name, supervisor_name)
        self.admin_supervisor_add_page.save_screenshot('admin_supervisor_add_page_save_blank_username.jpg')

        self.admin_supervisor_add_page.username.input('test003')
        self.admin_supervisor_add_page.password.input('test003')
        self.admin_supervisor_add_page.confirm_password.input('test003')

        self.admin_supervisor_add_page.save_add_another.click()
        self.admin_supervisor_add_page.redirect_back()

        self.assertions.assert_element_present([
            self.admin_supervisor_add_page.success,
            self.admin_supervisor_add_page.supervisor_name,
            self.admin_supervisor_add_page.username,
            self.admin_supervisor_add_page.email,
            self.admin_supervisor_add_page.active_start_date,
            self.admin_supervisor_add_page.active_end_date,
        ])
        self.assertions.assert_element_value(self.admin_supervisor_add_page.supervisor_name, "")
        self.admin_supervisor_add_page.save_screenshot('admin_supervisor_add_page_save_and_add.jpg')
        # endregion

        self.utils.time_elapsed('supervisor', self.timers)
