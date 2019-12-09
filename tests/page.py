#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import page, element
from . import container


class HomePage(page.HomePage):
    url_path = '/'
    angular = True

    def form_setup(self):
        super(HomePage, self).form_setup()
        self.top_nav_menu = container.DashboardNavMenu(self)
        self.error = element.Caption(self, css_selector='div.alert.alert-error', alias='Error Message')
        self.success = element.Caption(self, css_selector='div.alert.alert-success', alias='Success Message')
        # these are containers that will be refreshed when redirect is run for angular pages
        self.angular_containers += ['top_nav_menu', ]

    def update_controls(self):
        """Update controls for Wishlists Details"""

        super(HomePage, self).update_controls()
        # self.wishlists = self._update_control_group(container.WishlistDetailRow)
        # self.top_nav_menu = self._update_control_group(container.DashboardNavMenu)


class SigninPage(HomePage):
    url_path = '/static/index.html#/login'
    alias = "Login Page"

    def form_setup(self):
        super(SigninPage, self).form_setup()
        self.identification = element.TextBox(self, dom_id='username', alias='Username Textbox', angular=True)
        self.password = element.TextBox(self, dom_id='credentials', alias='Password Textbox', angular=True)
        self.submit = element.Button(self, css_selector='button.btn-primary', alias='Login Button', angular=True)


class LandingPage(HomePage):
    url_path = '/static/index.html'
    alias = "Landing Page"

    def form_setup(self):
        super(LandingPage, self).form_setup()
        self.job_menu = container.DashboardJobMenu(self)
        self.repair_menu = container.DashboardRepairMenu(self)
        # self.report_menu = container.DashboardReportMenu(self)


class JobListPage(HomePage):
    url_path = '/static/index.html#/job/list'
    alias = "Job List Page"

    def form_setup(self):
        super(JobListPage, self).form_setup()
        self.jobs = []

    def update_controls(self):
        super(JobListPage, self).update_controls()
        self.jobs = self._update_control_group(container.JobListItem)


class JobCreatePage(HomePage):
    url_path = '/static/index.html#/job/create'
    alias = "Job Create Page"

    def form_setup(self):
        super(JobCreatePage, self).form_setup()
        self.date_received = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='date_received']", alias="Date Received Ocom Input Datepicker")
        self.job_type = container.OcomInputSelectBox(self, css_selector="ocom-input[field-name='job_type']",
                                                     alias="Job Type Ocom Input Select")
        self.description = container.OcomInputTextArea(self, css_selector="ocom-input[field-name='description']",
                                                       alias="Description Ocom Input TextArea")
        self.comments = container.OcomInputTextArea(self, css_selector="ocom-input[field-name='comments']",
                                                    alias="Comments Ocom Input TextArea")
        self.address = container.OcomInputTextBox(self, css_selector="ocom-input[field-name='address']",
                                                  alias="Address Ocom Input TextBox")
        self.suburb = container.OcomInputTextBox(self, css_selector="ocom-input[field-name='suburb']",
                                                 alias="Suburb Ocom Input TextBox")
        self.client = container.OcomInputSelectBox(self, css_selector="ocom-input[field-name='client']",
                                                   alias="Client Ocom Input Select")
        self.purchase_order_number = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='purchase_order_number']",
            alias="Purchase Order No. Input TextBox")
        self.job_number = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='job_number']", alias="Job No. Input Select")
        self.purchase_order_value = container.OcomInputMoneyBox(
            self, css_selector="ocom-input[field-name='purchase_order_value']", alias="Purchase Order Value MoneyBox")
        self.sqm = container.OcomInputNumberBox(
            self, css_selector="ocom-input[field-name='sqm']", alias="SQM NumberBox")
        self.sub_contractor = container.OcomInputSelectBox(
            self, css_selector="ocom-input[field-name='sub_contractor']", alias="Sub-Contractor Input Select")
        self.estimated_cost = container.OcomInputMoneyBox(
            self, css_selector="ocom-input[field-name='estimated_cost']", alias="Estimated Cost Value MoneyBox")
        self.pour_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='pour_date']", alias="Pour Date Datepicker")
        self.supervisor = container.OcomInputSelectBox(
            self, css_selector="ocom-input[field-name='supervisor']", alias="Supervisor Input Select")
        self.supervisor_mobile_number = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='supervisor_mobile_number']",
            alias="Supervisor Mobile No. TextBox")
        self.supervisor_email = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='supervisor_email']", alias="Supervisor Email TextBox")
        self.base_inspection_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='base_inspection_date']", alias="Base Inspection Date Datepicker")
        self.steel_inspection_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='steel_inspection_date']", alias="Steel Inspection Datepicker")
        self.rock_m3 = container.OcomInputNumberBox(
            self, css_selector="ocom-input[field-name='rock_m3']", alias="Rock (m^3) NumberBox")
        self.rock_booked_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='rock_booked_date']", alias="Rock Booked Date Datepicker")
        self.materials = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='materials']", alias="Materials Datepicker")
        self.materials_time = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='materials_time']", alias="Materials Time TextBox")
        self.has_part_a = container.OcomInputCheckBox(
            self, css_selector="ocom-input[field-name='has_part_a']", alias="Has Part A Checkbox")
        self.part_a_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='part_a_date']", alias="Part A Date Datepicker")
        self.part_a_booking_no = container.OcomInputTextBox(
            self, css_selector="ocom-input[field-name='part_a_booking_no']", alias="Part A Booking No. TextBox")
        self.waste_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='waste_date']", alias="Waste Date Datepicker")
        self.piers_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='piers_date']", alias="Piers Date Datepicker")
        self.piers_inspection_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='piers_inspection_date']", alias="Piers Inspection Datepicker")
        self.piers_concrete_date = container.OcomInputDateTimePicker(
            self, css_selector="ocom-input[field-name='piers_concrete_date']", alias="Piers Concrete Datepicker")
        self.proposed_start_date = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='proposed_start_date']", alias="Proposed Start Datepicker")
        self.start_date = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='start_date']", alias="Actual Start Date Datepicker")
        self.end_date = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='end_date']", alias="End Date Datepicker")
        self.call_up_date = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='call_up_date']", alias="Call Up Date Datepicker")
        self.take_off_sent = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='take_off_sent']", alias="Take Off Sent Datepicker")
        self.paving_colour = container.OcomInputSelectBox(
            self, css_selector="ocom-input[field-name='paving_colour']", alias="Paving Colour Select")
        self.excavation_allowance = container.OcomInputNumberBox(
            self, css_selector="ocom-input[field-name='excavation_allowance']", alias="Excavation Allowance NumberBox")
        self.paving_type = container.OcomInputSelectBox(
            self, css_selector="ocom-input[field-name='paving_type']", alias="Paving Type Select")
        self.date_cancelled = container.OcomInputDatePicker(
            self, css_selector="ocom-input[field-name='date_cancelled']", alias="Date Cancelled Datepicker")
        self.drains = container.OcomInputNumberBox(
            self, css_selector="ocom-input[field-name='drains']", alias="Drains (m) NumberBox")
        self.drain_type = container.OcomInputSelectBox(
            self, css_selector="ocom-input[field-name='drain_type']", alias="Drain Type Select")
        self.dollars_difference = container.OcomInputMoneyBox(
            self, css_selector="ocom-input[field-name='dollars_difference']", alias="Dollars Difference MoneyBox")


class JobEditPage(JobCreatePage):
    url_path = '/static/index.html#/job/edit'
    alias = "Job Edit Page"


class AdminPage(HomePage):
    url_path = '/admin/'
    alias = "Admin Page"
    angular = False

    def form_setup(self):
        super(AdminPage, self).form_setup()
        self.error = element.Caption(self, css_selector='p.alert.alert-error', alias='Error Message', angular=True)
        self.success = element.Caption(self, css_selector='p.alert.alert-success', alias='Success Message',
                                       angular=True)
        self.code_tables = container.AdminDashboardCodeTables(self)
        self.modules = container.AdminDashboardModules(self)
        self.authentication = container.AdminDashboardAuthentication(self)
        self.top_nav_menu = container.AdminDashboardNavMenu(self)
        self.left_sidebar = container.AdminDashboardLeftSidebar(self)
        self.footer = container.AdminDashboardFooter(self)


class AdminListPage(HomePage):
    alias = "Admin List Page"
    angular = False

    def form_setup(self):
        super(AdminListPage, self).form_setup()
        self.error = element.Caption(self, css_selector='p.alert.alert-error', alias="Error Message", angular=True)
        self.success = element.Caption(self, css_selector='.alert.alert-success', alias="Success Message",
                                       angular=True)
        self.keyword = element.InputElement(self, dom_id='searchbar', alias="Keyword")
        self.active_status = element.DropDown(self, name='active_start_date', alias="Active Status Dropdown")
        self.active_start_date = element.DropDown(self, name='active_start_date__gte',
                                                  alias="Active Start Date Dropdown")
        self.active_end_date = element.DropDown(self, name='active_end_date__gte', alias="Active End Date Dropdown")
        self.search = element.Button(self, css_selector='input.submit', alias="Seatch Button")
        self.top_nav_menu = container.AdminDashboardNavMenu(self)
        self.left_sidebar = container.AdminDashboardLeftSidebar(self)
        self.footer = container.AdminDashboardFooter(self)
        self.add = element.LinkButton(self, css_selector='.object-tools > a', alias="Add Item Button")


class AdminAddPage(HomePage):
    alias = "Admin Add Page"
    angular = False

    def form_setup(self):
        super(AdminAddPage, self).form_setup()
        self.error = element.Caption(self, css_selector='div.alert.alert-error', alias="Error Message", angular=True)
        self.success = element.Caption(self, css_selector='div.alert.alert-success', alias="Success Message",
                                       angular=True)
        self.save = element.Button(self, css_selector='button[name="_save"]', alias="Save Button")
        self.save_and_continue = element.Button(self, css_selector='button[name="_continue"]',
                                                alias="Save And Continue Editing Button")
        self.save_add_another = element.Button(self, css_selector='button[name="_addanother"]',
                                               alias="Save And Add Another Button")
        self.active_start_date = element.TextBox(self, dom_id='id_active_start_date_0', alias="Active Start Date")
        self.active_start_time = element.TextBox(self, dom_id='id_active_start_date_1', alias="Active Start Time")
        self.active_end_date = element.TextBox(self, dom_id='id_active_end_date_0', alias="Active End Date")
        self.active_end_time = element.TextBox(self, dom_id='id_active_end_date_1', alias="Active End Time")
        self.tools = container.AdminFormTools(self)


class AdminClientListPage(AdminListPage):
    url_path = '/admin/api/client/'
    alias = "Admin Client List Page"

    def form_setup(self):
        super(AdminClientListPage, self).form_setup()
        self.client_name = element.Link(self, css_selector='#result_list th:nth-child(1) a',
                                        alias="Client Name Sort Link")
        self.xero_customer = element.Link(self, css_selector='#result_list th:nth-child(2) span',
                                          alias="Xero Customer Sort Link")
        self.send_invoices = element.Link(self, css_selector='#result_list th:nth-child(3) a',
                                          alias="Send Invoices Sort Link")
        self.part_a_required = element.Link(self, css_selector='#result_list th:nth-child(4) a',
                                            alias="Part A Required Sort Link")
        self.they_supply_pump = element.Link(self, css_selector='#result_list th:nth-child(5) a',
                                             alias="They Supply Pump Sort Link")
        self.active_start_date = element.Link(self, css_selector='#result_list th:nth-child(6) a',
                                              alias="Active Start Date Sort Link")
        self.active_end_date = element.Link(self, css_selector='#result_list th:nth-child(7) a',
                                            alias="Active End Date Sort Link")
        self.clients = []

    def update_controls(self):
        super(AdminClientListPage, self).update_controls()
        self.clients = self._update_control_group(container.AdminClientListItem)


class AdminClientAddPage(AdminAddPage):
    url_path = '/admin/api/client/add/'
    alias = "Admin Client Add Page"

    def form_setup(self):
        super(AdminClientAddPage, self).form_setup()
        self.client_name = element.TextBox(self, dom_id='id_name', alias="Client Name")
        self.xero_customer = element.TextBox(self, dom_id='id_xero_customer', alias="Xero Customer")
        self.send_invoices = element.CheckBox(self, dom_id='id_send_invoices', alias="Send Invoices Checkbox")
        self.suppliers = element.SelectListBox(self, dom_id='id_suppliers', alias="Suppliers List")
        self.part_a_required = element.CheckBox(self, dom_id='id_required_part_a', alias="Part A Required Checkbox")
        self.they_supply_pump = element.CheckBox(self, dom_id='id_they_supply_pump', alias="They Supply Pump Checkbox")


class AdminClientEditPage(AdminClientAddPage):
    alias = "Admin Client Edit Page"


class AdminSubbieListPage(AdminListPage):
    url_path = '/admin/api/subbie/'
    alias = "Admin Subbie List Page"

    def form_setup(self):
        super(AdminSubbieListPage, self).form_setup()
        self.subbie_name = element.Link(self, css_selector='#result_list th:nth-child(1) a',
                                        alias="Subbie Name Sort Link")
        self.type = element.Link(self, css_selector='#result_list th:nth-child(2) a', alias="Subbie Type Sort Link")
        self.has_xero = element.Caption(self, css_selector='#result_list th:nth-child(3) span', alias="Has Xero Text")
        self.username = element.Link(self, css_selector='#result_list th:nth-child(4) a', alias="Username Sort Link")
        self.email = element.Link(self, css_selector='#result_list th:nth-child(5) a', alias="Email Sort Link")
        self.active_start_date = element.Link(self, css_selector='#result_list th:nth-child(6) a',
                                              alias="Active Start Date Sort Link")
        self.active_end_date = element.Link(self, css_selector='#result_list th:nth-child(7) a',
                                            alias="Active End Date Sort Link")
        self.subbies = []

    def update_controls(self):
        super(AdminSubbieListPage, self).update_controls()
        self.subbies = self._update_control_group(container.AdminSubbieListItem)


class AdminSubbieAddPage(AdminAddPage):
    url_path = '/admin/api/subbie/add/'
    alias = "Admin Subbie Add Page"

    def form_setup(self):
        super(AdminSubbieAddPage, self).form_setup()
        self.subbie_name = element.TextBox(self, dom_id='id_name', alias="Subbie Name")
        self.type = element.DropDown(self, dom_id='id_type', alias="Subbie Type")
        self.xero_supplier = element.DropDown(self, dom_id='id_xero_supplier', alias="Xero Supplier")
        self.rate_per_meter = element.TextBox(self, dom_id='id_rate_per_m', alias="Rate per meter")
        self.jobs_per_day = element.TextBox(self, dom_id='id_jobs_per_day', alias="Jobs per day")
        self.can_see_plans_before_accept = element.CheckBox(self, dom_id='id_can_see_plans_before_accept',
                                                            alias="Can See Plans Before Accept Checkbox")
        self.account_collapser = element.Link(self, dom_id='fieldsetcollapser0', alias="Account Collapser Link")
        self.username = element.TextBox(self, dom_id='id_username', alias="Username")
        self.password = element.TextBox(self, dom_id='id_password', alias="Password")
        self.confirm_password = element.TextBox(self, dom_id='id_confirm_password', alias="Confirm Password")
        self.email = element.TextBox(self, dom_id='id_email', alias="Email")
        self.enabled = element.CheckBox(self, dom_id='id_enabled', alias="Enabled")


class AdminSubbieEditPage(AdminSubbieAddPage):
    alias = "Admin Subbie Edit Page"


class AdminSupervisorListPage(AdminListPage):
    url_path = '/admin/api/supervisor/'
    alias = "Admin Supervisor List Page"

    def form_setup(self):
        super(AdminSupervisorListPage, self).form_setup()
        self.supervisor_name = element.Link(self, css_selector='#result_list th:nth-child(1) a',
                                            alias="Supervisor Name Sort Link")
        self.username = element.Link(self, css_selector='#result_list th:nth-child(2) a', alias="Username Sort Link")
        self.email = element.Link(self, css_selector='#result_list th:nth-child(3) a', alias="Email Sort Link")
        self.active_start_date = element.Link(self, css_selector='#result_list th:nth-child(4) a',
                                              alias="Active Start Date Sort Link")
        self.active_end_date = element.Link(self, css_selector='#result_list th:nth-child(5) a',
                                            alias="Active End Date Sort Link")
        self.supervisors = []

    def update_controls(self):
        super(AdminSupervisorListPage, self).update_controls()
        self.supervisors = self._update_control_group(container.AdminSupervisorListItem)


class AdminSupervisorAddPage(AdminAddPage):
    url_path = '/admin/api/supervisor/add/'
    alias = "Admin Supervisor Add Page"

    def form_setup(self):
        super(AdminSupervisorAddPage, self).form_setup()
        self.supervisor_name = element.TextBox(self, dom_id='id_name', alias="Supervisor Name")
        self.account_collapser = element.Link(self, dom_id='fieldsetcollapser0', alias="Account Collapser Link")
        self.username = element.TextBox(self, dom_id='id_username', alias="Username")
        self.password = element.TextBox(self, dom_id='id_password', alias="Password")
        self.confirm_password = element.TextBox(self, dom_id='id_confirm_password', alias="Confirm Password")
        self.email = element.TextBox(self, dom_id='id_email', alias="Email")
        self.phone_number = element.TextBox(self, dom_id='id_phone_number', alias="Phone Number")
        self.enabled = element.CheckBox(self, dom_id='id_enabled', alias="Enabled")


class AdminSupervisorEditPage(AdminSupervisorAddPage):
    alias = "Admin Supervisor Edit Page"


class AdminSigninPage(AdminPage):
    url_path = '/admin/login/'
    alias = "Admin Signin Page"

    def form_setup(self):
        super(AdminSigninPage, self).form_setup()
        self.identification = element.TextBox(self, dom_id='id_username', alias='Username Textbox', angular=True)
        self.password = element.TextBox(self, dom_id='id_password', alias='Password Textbox', angular=True)
        self.submit = element.Button(self, css_selector='.submit-row input.btn-info', alias='Login Button',
                                     angular=True)


class AdminSignoutPage(AdminPage):
    url_path = '/admin/logout/'
    alias = "Admin Signout Page"

    def form_setup(self):
        super(AdminSignoutPage, self).form_setup()
        self.message = element.Caption(self, css_selector='h3.italic-title', alias='Signout Page Message', angular=True)
