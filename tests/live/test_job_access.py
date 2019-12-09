"""tests.live.test_job_access.py - Job Access Tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

# from django.utils import timezone
from django.test import override_settings
from ocom.tests import app
from tests import fixtures, page


@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher', ))
class JobAccessTest(app.OcomLiveServerTestCaseNoFixtures):
    heading = "---Job Access test---"
    always_reset_browser = False

    @classmethod
    def setUpClass(cls):
        cls.factory = fixtures.Sampler()
        super(JobAccessTest, cls).setUpClass()

    def setUp(self):
        super(JobAccessTest, self).setUp()
        self.login_page = page.SigninPage(self)
        self.landing_page = page.LandingPage(self)
        self.job_list_page = page.JobListPage(self)
        self.job_create_page = page.JobCreatePage(self)

    def test_job_list(self):
        # region pre-test routines
        self.utils.start_timer('job_list', self.timers, "Checking Job List page...")
        user = self.factory.user(password=self.common_password)
        self.factory.role(user=user, administrator=True)
        client_a = self.factory.client()
        client_b = self.factory.client()
        slab = self.factory.job_type(code='slab', description="Slab")
        excavation = self.factory.job_type(code='excavation', description="Excavation")
        # endregion

        # region proceed to job list page
        self.login_page.navigate()
        self.login_page.identification.input(user.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.landing_page.job_menu.list.click(timeout=1)
        self.job_list_page.redirect(update_controls=False)
        self.job_list_page.loading_bar.wait_until_removed()
        self.job_list_page.update_controls()
        self.assertions.assert_true(len(self.job_list_page.jobs) == 0,
                                    "Asserting that Job List Page is empty...")
        self.job_list_page.save_html('job_list_page_start.html')
        self.job_list_page.save_screenshot('job_list_page_start.jpg')
        # endregion

        # region add job fixtures and check list
        self.factory.job(client=client_a, job_type=slab, suburb="Some Suburb")
        self.job_list_page.refresh(timeout=1, update_controls=False)
        self.job_list_page.loading_bar.wait_until_removed()
        self.job_list_page.update_controls()
        self.job_list_page.save_screenshot('job_list_page_one_entry.jpg')
        self.assertions.assert_true(len(self.job_list_page.jobs) == 1,
                                    "Asserting that Job List Page is NOT empty...")

        # add more
        self.factory.job(client=client_b, job_type=slab, suburb="Some Suburb")
        self.factory.job(client=client_b, job_type=slab, suburb="Some Suburb")
        self.factory.job(client=client_a, job_type=excavation, suburb="Some Suburb")
        self.factory.job(client=client_b, job_type=excavation, suburb="Some Suburb")
        self.job_list_page.refresh(timeout=1, update_controls=False)
        self.job_list_page.loading_bar.wait_until_removed()
        self.job_list_page.update_controls()
        self.job_list_page.save_screenshot('job_list_page_five_entries.jpg')
        self.assertions.assert_true(len(self.job_list_page.jobs) == 5,
                                    "Asserting that Job List Page has 5 entries...")
        # endregion

        self.utils.time_elapsed('job_list', self.timers)

    def test_job_create(self):
        # region pre-test routines
        self.utils.start_timer('job_create', self.timers, "Checking Job Create page...")
        user = self.factory.user(password=self.common_password)
        self.factory.role(user=user, administrator=True)
        # endregion

        # region proceed to job list page
        self.login_page.navigate()
        self.login_page.identification.input(user.username)
        self.login_page.password.input(self.common_password)
        self.login_page.submit.click(timeout=1)
        self.landing_page.redirect()

        self.landing_page.job_menu.new.click(timeout=1)
        self.job_create_page.redirect(update_controls=False)
        self.job_create_page.loading_bar.wait_until_removed()
        self.job_create_page.update_controls()

        self.assertions.assert_element_present([
            self.job_create_page.date_received,
            self.job_create_page.job_type,
            self.job_create_page.description,
            self.job_create_page.comments,
            self.job_create_page.address,
            self.job_create_page.suburb,
            self.job_create_page.client,
            self.job_create_page.purchase_order_number,
            self.job_create_page.job_number,
            self.job_create_page.purchase_order_value,
            self.job_create_page.sqm,
            self.job_create_page.sub_contractor,
            self.job_create_page.estimated_cost,
            self.job_create_page.pour_date,
            self.job_create_page.supervisor,
            self.job_create_page.supervisor_mobile_number,
            self.job_create_page.supervisor_email,
            self.job_create_page.base_inspection_date,
            self.job_create_page.steel_inspection_date,
            self.job_create_page.rock_m3,
            self.job_create_page.rock_booked_date,
            self.job_create_page.materials,
            self.job_create_page.materials_time,
            self.job_create_page.has_part_a,
            # self.job_create_page.part_a_date,
            # self.job_create_page.part_a_booking_no,
            self.job_create_page.waste_date,
            self.job_create_page.piers_date,
            self.job_create_page.piers_inspection_date,
            self.job_create_page.piers_concrete_date,
            self.job_create_page.proposed_start_date,
            self.job_create_page.start_date,
            self.job_create_page.end_date,
            self.job_create_page.call_up_date,
            self.job_create_page.take_off_sent,
            self.job_create_page.paving_colour,
            self.job_create_page.excavation_allowance,
            self.job_create_page.paving_type,
            self.job_create_page.date_cancelled,
            self.job_create_page.drains,
            self.job_create_page.drain_type,
            self.job_create_page.dollars_difference,
        ])
        self.job_create_page.save_html('job_create_page_start.html')
        self.job_create_page.save_screenshot('job_create_page_start.jpg')
        # endregion

        self.utils.time_elapsed('job_create', self.timers)
