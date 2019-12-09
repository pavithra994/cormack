"""tests.standard.test_api_access - API Access Tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import app
from tests import api, fixtures


class ApiAccessTest(app.OcomTestCaseNoFixtures):
    heading = "---Cormack API access test---"

    def test_code_tables(self):
        # region pre-test routines
        self.utils.start_timer('code_tables', self.timers, "Checking Code Table API end-points...")
        user_with_role = self.factory.user(password=self.common_password)
        self.factory.role(user=user_with_role)
        self.auth_api = api.AuthTokenApi(self)
        self.drain_type_api = api.CodeDrainTypeApi(self)
        self.file_type_api = api.CodeFileTypeApi(self)
        self.job_type_api = api.CodeJobTypeApi(self)
        self.paving_colour_api = api.CodePavingColourApi(self)
        self.paving_type_api = api.CodePavingTypeApi(self)
        self.repair_type_api = api.CodeRepairTypeApi(self)
        self.subbie_type_api = api.CodeSubbieTypeApi(self)
        self.task_type_api = api.CodeTaskTypeApi(self)
        table_data = {
            'code': 'TEST',
            'description': "Test Data"
        }
        self.auth_api.authenticate(username=user_with_role.username, password=self.common_password)
        # endregion

        # region drain type
        self.drain_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.drain_type_api.status_code, 200,
                                     "Asserting presence of list for Code Drain Type API...")
        self.assertions.assert_true(len(self.drain_type_api.content) == 0,
                                    "Asserting empty list for Code Drain Type API...")
        self.factory.drain_type()
        self.factory.drain_type()
        self.factory.drain_type()
        self.drain_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.drain_type_api.content) == 3,
                                    "Asserting list for Code Drain Type API contains three items...")
        self.drain_type_api.post(table_data, message="Adding Drain type thru POST...", token=self.auth_api.token)
        self.drain_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.drain_type_api.content) == 4,
                                    "Asserting list for Code Drain Type API contains four items...")
        self.drain_type_api.post(table_data, message="Adding same Drain type thru POST...", token=self.auth_api.token)
        self.drain_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.drain_type_api.content) == 4,
                                    "Asserting list for Code Drain Type API stays at four items...")
        # endregion

        # region file type
        self.file_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.file_type_api.status_code, 200,
                                     "Asserting presence of list for Code File Type API...")
        self.assertions.assert_true(len(self.file_type_api.content) == 0,
                                    "Asserting empty list for Code File Type API...")
        self.factory.file_type()
        self.factory.file_type()
        self.factory.file_type()
        self.file_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.file_type_api.content) == 3,
                                    "Asserting list for Code File Type API contains three items...")
        self.file_type_api.post(table_data, message="Adding File Type thru POST...", token=self.auth_api.token)
        self.file_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.file_type_api.content) == 4,
                                    "Asserting list for Code File Type API contains four items...")
        self.file_type_api.post(table_data, message="Adding same File type thru POST...", token=self.auth_api.token)
        self.file_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.file_type_api.content) == 4,
                                    "Asserting list for Code File Type API stays at four items...")
        # endregion

        # region job type
        self.job_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.job_type_api.status_code, 200,
                                     "Asserting presence of list for Code Job Type API...")
        self.assertions.assert_true(len(self.job_type_api.content) == 0,
                                    "Asserting empty list for Code Job Type API...")
        self.factory.job_type()
        self.factory.job_type()
        self.factory.job_type()
        self.job_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.job_type_api.content) == 3,
                                    "Asserting list for Code Job Type API contains three items...")
        self.job_type_api.post(table_data, message="Adding Job Type thru POST...", token=self.auth_api.token)
        self.job_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.job_type_api.content) == 4,
                                    "Asserting list for Code Job Type API contains four items...")
        self.job_type_api.post(table_data, message="Adding same Job type thru POST...", token=self.auth_api.token)
        self.job_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.job_type_api.content) == 4,
                                    "Asserting list for Code Job Type API stays at four items...")
        # endregion

        # region paving colour
        self.paving_colour_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.paving_colour_api.status_code, 200,
                                     "Asserting presence of list for Code Paving Coiour API...")
        self.assertions.assert_true(len(self.paving_colour_api.content) == 0,
                                    "Asserting empty list for Code Paving Coiour API...")
        self.factory.paving_colour()
        self.factory.paving_colour()
        self.factory.paving_colour()
        self.paving_colour_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_colour_api.content) == 3,
                                    "Asserting list for Code Paving Coiour API contains three items...")
        self.paving_colour_api.post(table_data, message="Adding Paving Colour thru POST...", token=self.auth_api.token)
        self.paving_colour_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_colour_api.content) == 4,
                                    "Asserting list for Code Paving Colour API contains four items...")
        self.paving_colour_api.post(table_data, message="Adding same Paving colour thru POST...",
                                    token=self.auth_api.token)
        self.paving_colour_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_colour_api.content) == 4,
                                    "Asserting list for Code Paving Colour API stays at four items...")
        # endregion

        # region paving type
        self.paving_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.paving_type_api.status_code, 200,
                                     "Asserting presence of list for Code Paving Type API...")
        self.assertions.assert_true(len(self.paving_type_api.content) == 0,
                                    "Asserting empty list for Code Paving Type API...")
        self.factory.paving_type()
        self.factory.paving_type()
        self.factory.paving_type()
        self.paving_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_type_api.content) == 3,
                                    "Asserting list for Code Paving Type API contains three items...")
        self.paving_type_api.post(table_data, message="Adding Paving Type thru POST...", token=self.auth_api.token)
        self.paving_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_type_api.content) == 4,
                                    "Asserting list for Code Paving Type API contains four items...")
        self.paving_type_api.post(table_data, message="Adding same Paving type thru POST...", token=self.auth_api.token)
        self.paving_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.paving_type_api.content) == 4,
                                    "Asserting list for Code Paving Type API stays at four items...")
        # endregion

        # region repair type
        self.repair_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.repair_type_api.status_code, 200,
                                     "Asserting presence of list for Code Repair Type API...")
        self.assertions.assert_true(len(self.repair_type_api.content) == 0,
                                    "Asserting empty list for Code Repair Type API...")
        self.factory.repair_type()
        self.factory.repair_type()
        self.factory.repair_type()
        self.repair_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.repair_type_api.content) == 3,
                                    "Asserting list for Code Repair Type API contains three items...")
        self.repair_type_api.post(table_data, message="Adding Repair Type thru POST...", token=self.auth_api.token)
        self.repair_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.repair_type_api.content) == 4,
                                    "Asserting list for Code Repair Type API contains four items...")
        self.repair_type_api.post(table_data, message="Adding same Repair type thru POST...", token=self.auth_api.token)
        self.repair_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.repair_type_api.content) == 4,
                                    "Asserting list for Code Repair Type API stays at four items...")
        # endregion

        # region subbie type
        self.subbie_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.subbie_type_api.status_code, 200,
                                     "Asserting presence of list for Code Subbie Type API...")
        self.assertions.assert_true(len(self.subbie_type_api.content) == 0,
                                    "Asserting empty list for Code Subbie Type API...")
        self.factory.subbie_type()
        self.factory.subbie_type()
        self.factory.subbie_type()
        self.subbie_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.subbie_type_api.content) == 3,
                                    "Asserting list for Code Subbie Type API contains three items...")
        self.subbie_type_api.post(table_data, message="Adding Subbie Type thru POST...", token=self.auth_api.token)
        self.subbie_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.subbie_type_api.content) == 4,
                                    "Asserting list for Code Subbie Type API contains four items...")
        self.subbie_type_api.post(table_data, message="Adding same Subbie type thru POST...", token=self.auth_api.token)
        self.subbie_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.subbie_type_api.content) == 4,
                                    "Asserting list for Code Subbie Type API stays at four items...")
        # endregion

        # region task type
        self.task_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.task_type_api.status_code, 200,
                                     "Asserting presence of list for Code Task Type API...")
        self.assertions.assert_true(len(self.task_type_api.content) == 0,
                                    "Asserting empty list for Code Task Type API...")
        self.factory.task_type()
        self.factory.task_type()
        self.factory.task_type()
        self.task_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.task_type_api.content) == 3,
                                    "Asserting list for Code Task Type API contains three items...")
        self.task_type_api.post(table_data, message="Adding Task Type thru POST...", token=self.auth_api.token)
        self.task_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.task_type_api.content) == 4,
                                    "Asserting list for Code Task Type API contains four items...")
        self.task_type_api.post(table_data, message="Adding same Task type thru POST...", token=self.auth_api.token)
        self.task_type_api.navigate(token=self.auth_api.token)
        self.assertions.assert_true(len(self.task_type_api.content) == 4,
                                    "Asserting list for Code Task Type API stays at four items...")
        # endregion

        self.utils.time_elapsed('code_tables', self.timers)

    def test_basic_security(self):
        # region pre-test routines
        self.utils.start_timer('security', self.timers, "Checking security of API end-points...")
        user = self.factory.user(password=self.common_password)
        user_with_role = self.factory.user(password=self.common_password)
        self.factory.role(administrator=True, user=user_with_role)
        self.auth_api = api.AuthTokenApi(self)
        self.client_api = api.ClientApi(self)
        self.role_api = api.RoleApi(self)
        self.factory.client()
        # endregion

        # region no auth
        self.client_api.navigate()
        self.assertions.assert_equal(self.client_api.status_code, 403,
                                     "Asserting non-authentication for Client API...")
        # endregion

        # region with invalid auth
        self.auth_api.authenticate(username='nonexistent', password='something')
        self.assertions.assert_equal(self.auth_api.status_code, 400,
                                     "Asserting non-authentication for Auth token...")
        # endregion

        # region with valid auth but no role
        self.auth_api.authenticate(username=user.username, password=self.common_password)
        self.assertions.assert_equal(self.auth_api.status_code, 200,
                                     "Asserting authentication for Auth token with user...")

        self.client_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.client_api.status_code, 200,
                                     "Asserting presence of list for Client API...")
        self.assertions.assert_true(len(self.client_api.content) == 0,  "Asserting empty list for Client API...")
        self.role_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.role_api.status_code, 200, "Asserting presence of list for Role API...")
        # endregion

        # region with valid auth and role
        self.auth_api.authenticate(username=user_with_role.username, password=self.common_password)
        self.assertions.assert_equal(self.auth_api.status_code, 200,
                                     "Asserting authentication for Auth token with user...")

        self.client_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.client_api.status_code, 200,
                                     "Asserting presence of list for Client API...")
        self.assertions.assert_true(len(self.client_api.content) > 0,  "Asserting list shown for Client API...")
        self.role_api.navigate(token=self.auth_api.token)
        self.assertions.assert_equal(self.role_api.status_code, 200, "Asserting presence of list for Role API...")
        # endregion

        self.utils.time_elapsed('security', self.timers)

    @classmethod
    def setUpClass(cls):
        cls.factory = fixtures.Sampler()
        super(ApiAccessTest, cls).setUpClass()
