"""tests.standard.test_admin_access - Admin Access Tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import app
from tests import fixtures, simple_page as page


class AdminAccessTest(app.OcomTestCaseNoFixtures):
    heading = "---Admin access test---"

    def test_dashboard_access(self):
        # region pre-test routines
        self.dashboard_page = page.DashboardPage(self)
        # endregion

        # region dashboard
        self.dashboard_page.navigate()
        self.assertions.assert_equal(self.dashboard_page.status_code, 302, "Asserting redirect for Dashboard Page...")
        # endregion

    def test_admin_login(self):
        # region pre-test routines
        self.utils.start_timer('login', self.timers, "Checking regular login...")
        self.dashboard_page = page.DashboardPage(self)
        self.login_page = page.SigninPage(self)
        # endregion

        # region non-existent account
        self.dashboard_page.navigate()
        self.dashboard_page.login('thisisatest', self.common_password, '/admin')
        self.assertions.assert_contains(
            self.dashboard_page.content,
            "Please enter the correct username and password for a staff account",
            "Asserting error message on log in of non-existent account...")
        # endregion

        # region regular account
        user = self.factory.user(password=self.common_password)
        self.dashboard_page.login(user.username, self.common_password, '/admin')
        self.assertions.assert_equal(self.dashboard_page.status_code, 200, "Asserting no redirect on sign in...")
        self.assertions.assert_contains(
            self.dashboard_page.content,
            "Please enter the correct username and password for a staff account",
            "Asserting error message on log in of regular account...")
        # endregion

        # region admin account
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        self.assertions.assert_not_contains(
            self.dashboard_page.content,
            "Please enter the correct username and password for a staff account",
            "Asserting NO error message on log in of admin account...")
        # endregion

        self.utils.time_elapsed('login', self.timers)

    def test_admin_logout(self):
        # region pre-test routines
        self.utils.start_timer('logout', self.timers, "Checking admin logout...")
        self.dashboard_page = page.DashboardPage(self)
        # endregion

        # region admin account
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        self.dashboard_page.logout()
        self.assertions.assert_equal(self.dashboard_page.status_code, 200, "Asserting no redirect on sign out...")
        self.assertions.assert_contains(
            self.dashboard_page.content,
            "Thanks for spending some quality time with the Cormack JMS Admin Dashboard today.",
            "Asserting signout message on log out of admin account...")
        # endregion

        self.utils.time_elapsed('logout', self.timers)

    def test_admin_landing_page(self):
        # region pre-test routines
        self.utils.start_timer('home', self.timers, "Checking admin landing page...")
        self.dashboard_page = page.DashboardPage(self)
        # endregion

        # region admin account
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        self.assertions.assert_contains(self.dashboard_page.content, "/admin/api/client/add/",
                                        "Asserting Job link is present...")
        self.assertions.assert_contains(self.dashboard_page.content, "/admin/api/role/add/",
                                        "Asserting Role link is present...")
        # endregion

        self.utils.time_elapsed('home', self.timers)

    def test_admin_client_page(self):
        # region pre-test routines
        self.utils.start_timer('client', self.timers, "Checking Client admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.client_page = page.ClientPage(self)
        self.client_add_page = page.ClientAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.client.click()
        self.client_page.redirect()
        self.assertions.assert_equal(self.client_page.status_code, 200, "Asserting Client Page is accessible...")
        # endregion

        # region Client: Add
        self.client_page.add_link.click()
        self.client_add_page.redirect()
        self.assertions.assert_equal(self.client_add_page.status_code, 200,
                                     "Asserting Client Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('client', self.timers)

    def test_admin_drain_type_page(self):
        # region pre-test routines
        self.utils.start_timer('drain_type', self.timers, "Checking Code Table->Drain Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.drain_type_page = page.DrainTypePage(self)
        self.drain_type_add_page = page.DrainTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.drain_type.click()
        self.drain_type_page.redirect()
        self.assertions.assert_equal(self.drain_type_page.status_code, 200,
                                     "Asserting Drain Type Page is accessible...")
        # endregion

        # region Client: Add
        self.drain_type_page.add_link.click()
        self.drain_type_add_page.redirect()
        self.assertions.assert_equal(self.drain_type_add_page.status_code, 200,
                                     "Asserting Drain Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('drain_type', self.timers)

    def test_admin_file_type_page(self):
        # region pre-test routines
        self.utils.start_timer('file_type', self.timers, "Checking Code Table->File Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.file_type_page = page.FileTypePage(self)
        self.file_type_add_page = page.FileTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.file_type.click()
        self.file_type_page.redirect()
        self.assertions.assert_equal(self.file_type_page.status_code, 200,
                                     "Asserting File Type Page is accessible...")
        # endregion

        # region Client: Add
        self.file_type_page.add_link.click()
        self.file_type_add_page.redirect()
        self.assertions.assert_equal(self.file_type_add_page.status_code, 200,
                                     "Asserting File Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('file_type', self.timers)

    def test_admin_job_type_page(self):
        # region pre-test routines
        self.utils.start_timer('job_type', self.timers, "Checking Code Table->Job Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.job_type_page = page.JobTypePage(self)
        self.job_type_add_page = page.JobTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.job_type.click()
        self.job_type_page.redirect()
        self.assertions.assert_equal(self.job_type_page.status_code, 200,
                                     "Asserting Job Type Page is accessible...")
        # endregion

        # region Client: Add
        self.job_type_page.add_link.click()
        self.job_type_add_page.redirect()
        self.assertions.assert_equal(self.job_type_add_page.status_code, 200,
                                     "Asserting Job Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('job_type', self.timers)

    def test_admin_paving_colour_page(self):
        # region pre-test routines
        self.utils.start_timer('paving_colour', self.timers, "Checking Code Table->Paving Colour admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.paving_colour_page = page.PavingColourPage(self)
        self.paving_colour_add_page = page.PavingColourAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.paving_colour.click()
        self.paving_colour_page.redirect()
        self.assertions.assert_equal(self.paving_colour_page.status_code, 200,
                                     "Asserting Paving Colour Page is accessible...")
        # endregion

        # region Client: Add
        self.paving_colour_page.add_link.click()
        self.paving_colour_add_page.redirect()
        self.assertions.assert_equal(self.paving_colour_add_page.status_code, 200,
                                     "Asserting Paving Colour Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('paving_colour', self.timers)

    def test_admin_paving_type_page(self):
        # region pre-test routines
        self.utils.start_timer('paving_type', self.timers, "Checking Code Table->Paving Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.paving_type_page = page.PavingTypePage(self)
        self.paving_type_add_page = page.PavingTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.paving_type.click()
        self.paving_type_page.redirect()
        self.assertions.assert_equal(self.paving_type_page.status_code, 200,
                                     "Asserting Paving Type Page is accessible...")
        # endregion

        # region Client: Add
        self.paving_type_page.add_link.click()
        self.paving_type_add_page.redirect()
        self.assertions.assert_equal(self.paving_type_add_page.status_code, 200,
                                     "Asserting Paving Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('paving_type', self.timers)

    def test_admin_repair_type_page(self):
        # region pre-test routines
        self.utils.start_timer('repair_type', self.timers, "Checking Code Table->Repair Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.repair_type_page = page.RepairTypePage(self)
        self.repair_type_add_page = page.RepairTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.repair_type.click()
        self.repair_type_page.redirect()
        self.assertions.assert_equal(self.repair_type_page.status_code, 200,
                                     "Asserting Repair Type Page is accessible...")
        # endregion

        # region Client: Add
        self.repair_type_page.add_link.click()
        self.repair_type_add_page.redirect()
        self.assertions.assert_equal(self.repair_type_add_page.status_code, 200,
                                     "Asserting Repair Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('repair_type', self.timers)

    def test_admin_subbie_type_page(self):
        # region pre-test routines
        self.utils.start_timer('subbie_type', self.timers, "Checking Code Table->Subbie Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.subbie_type_page = page.SubbieTypePage(self)
        self.subbie_type_add_page = page.SubbieTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.subbie_type.click()
        self.subbie_type_page.redirect()
        self.assertions.assert_equal(self.subbie_type_page.status_code, 200,
                                     "Asserting Subbie Type Page is accessible...")
        # endregion

        # region Client: Add
        self.subbie_type_page.add_link.click()
        self.subbie_type_add_page.redirect()
        self.assertions.assert_equal(self.subbie_type_add_page.status_code, 200,
                                     "Asserting Subbie Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('subbie_type', self.timers)

    def test_admin_task_type_page(self):
        # region pre-test routines
        self.utils.start_timer('task_type', self.timers, "Checking Code Table->Task Type admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.task_type_page = page.TaskTypePage(self)
        self.task_type_add_page = page.TaskTypeAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.task_type.click()
        self.task_type_page.redirect()
        self.assertions.assert_equal(self.task_type_page.status_code, 200,
                                     "Asserting Task Type Page is accessible...")
        # endregion

        # region Client: Add
        self.task_type_page.add_link.click()
        self.task_type_add_page.redirect()
        self.assertions.assert_equal(self.task_type_add_page.status_code, 200,
                                     "Asserting Task Type Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('task_type', self.timers)

    def test_admin_subbie_page(self):
        # region pre-test routines
        self.utils.start_timer('subbie', self.timers, "Checking Code Table->Subbie admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.subbie_page = page.SubbiePage(self)
        self.subbie_add_page = page.SubbieAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.subbie.click()
        self.subbie_page.redirect()
        self.assertions.assert_equal(self.subbie_page.status_code, 200,
                                     "Asserting Subbie Page is accessible...")
        # endregion

        # region Client: Add
        self.subbie_page.add_link.click()
        self.subbie_add_page.redirect()
        self.assertions.assert_equal(self.subbie_add_page.status_code, 200,
                                     "Asserting Subbie Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('subbie', self.timers)

    def test_admin_supervisor_page(self):
        # region pre-test routines
        self.utils.start_timer('supervisor', self.timers, "Checking Code Table->Supervisor admin page...")
        self.dashboard_page = page.DashboardPage(self)
        self.supervisor_page = page.SupervisorPage(self)
        self.supervisor_add_page = page.SupervisorAddPage(self)
        superuser = self.factory.user(password=self.common_password, superuser=True)
        self.dashboard_page.login(superuser.username, self.common_password, '/admin')
        # endregion

        # region Client: Change
        self.dashboard_page.content_links.supervisor.click()
        self.supervisor_page.redirect()
        self.assertions.assert_equal(self.supervisor_page.status_code, 200,
                                     "Asserting Supervisor Page is accessible...")
        # endregion

        # region Client: Add
        self.supervisor_page.add_link.click()
        self.supervisor_add_page.redirect()
        self.assertions.assert_equal(self.supervisor_add_page.status_code, 200,
                                     "Asserting Supervisor Add Page is accessible...")
        # endregion

        self.utils.time_elapsed('supervisor', self.timers)

    @classmethod
    def setUpClass(cls):
        cls.factory = fixtures.Sampler()
        super(AdminAccessTest, cls).setUpClass()
