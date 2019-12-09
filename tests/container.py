#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import element, container


class AdminDashboardFooter(container.AdminDashboardFooter):
    def controls_setup(self):
        """Footer controls"""

        super(AdminDashboardFooter, self).controls_setup()
        self.version = element.Caption(self, alias="Cormack Version", css_selector='.copyright')


class AdminDashboardNavMenu(container.AdminDashboardNavMenu):
    alias = "Cormack Admin Dashboard Nav Menu"


class AdminDashboardLeftSidebar(container.AdminDashboardLeftSidebar):
    alias = "Cormack Admin Left Sidebar"


class AdminDashboardCodeTables(container.Container):
    alias = "Cormack Admin Dashboard Code Tables"
    css_selector = 'table.code_tables'

    def controls_setup(self):
        """Dashboard Code Table controls"""

        self.drain_types = container.AdminDashboardSubmodule(
            self, alias="Drain Types Submodule",
            css_selector='tr.CodeDrainType')
         self.depot_types = container.AdminDashboardSubmodule(
            self, alias="Depot Types Submodule",
            css_selector='tr.CodeJobType')
        self.file_types = container.AdminDashboardSubmodule(
            self, alias="File Types Submodule",
            css_selector='tr.CodeFileType')
        self.job_types = container.AdminDashboardSubmodule(
            self, alias="Job Types Submodule",
            css_selector='tr.CodeJobType')
        self.paving_colours = container.AdminDashboardSubmodule(
            self, alias="Paving Colours Submodule",
            css_selector='tr.CodePavingColour')
        self.paving_types = container.AdminDashboardSubmodule(
            self, alias="Paving Types Submodule",
            css_selector='tr.CodePavingType')
        self.repair_types = container.AdminDashboardSubmodule(
            self, alias="Repair Types Submodule",
            css_selector='tr.CodeRepairType')
        self.subbie_types = container.AdminDashboardSubmodule(
            self, alias="Subbie Types Submodule",
            css_selector='tr.CodeSubbieType')
        self.task_types = container.AdminDashboardSubmodule(
            self, alias="Task Types Submodule",
            css_selector='tr.CodeTaskType')
        

class AdminDashboardModules(container.Container):
    alias = "Cormack Admin Dashboard Page Modules"
    css_selector = 'table.modules'
    # element_as_source = True

    def controls_setup(self):
        """Dashboard Module controls"""

        self.clients = container.AdminDashboardSubmodule(
            self, alias="Clients Submodule",
            css_selector='tr.Client')
        self.subbies = container.AdminDashboardSubmodule(
            self, alias="Subbies Submodule",
            css_selector='tr.Subbie')
        self.supervisors = container.AdminDashboardSubmodule(
            self, alias="Supervisors Submodule",
            css_selector='tr.Supervisor')


class AdminDashboardAuthentication(container.Container):
    alias = "Cormack Admin Dashboard Page Authentication"
    css_selector = 'table.authentication'
    element_as_source = True

    def controls_setup(self):
        """Dashboard Auth controls"""

        self.roles = container.AdminDashboardSubmodule(
            self, alias="Users And Roles Submodule",
            css_selector='tr.Role')


class AdminClientListItem(container.Container):
    alias = "Admin Client List Item"
    css_selector = '#result_list > tbody > tr'
    element_as_source = True

    def controls_setup(self):
        """Admin Client List Item controls"""

        self.client_name = element.Link(self, css_selector='th:nth-child(1) > a', alias="Admin Client Name Link")
        self.xero_customer = element.Caption(self, css_selector='td:nth-child(2)', alias="Xero Customer")
        self.send_invoices = element.Image(self, css_selector='td:nth-child(3) img', alias="Send Invoices Check Mark")
        self.part_a_required = element.Image(self, css_selector='td:nth-child(4) img',
                                             alias="Part A Required Check Mark")
        self.they_supply_pump = element.Image(self, css_selector='td:nth-child(5) img',
                                              alias="They Supply Pump Check Mark")
        self.active_start_date = element.Link(self, css_selector='td:nth-child(6)', alias="Active Start Date Text")
        self.active_end_date = element.Link(self, css_selector='td:nth-child(6)', alias="Active End Date Text")


class AdminSubbieListItem(container.Container):
    alias = "Admin Subbie List Item"
    css_selector = '#result_list > tbody > tr'
    element_as_source = True

    def controls_setup(self):
        """Admin Subbie List Item controls"""

        self.subbie_name = element.Link(self, css_selector='th:nth-child(1) > a', alias="Admin Subbie Name Link")
        self.type = element.Caption(self, css_selector='td:nth-child(2)', alias="Subbie Type")
        self.username = element.Caption(self, css_selector='td:nth-child(3)', alias="Username")
        self.email = element.Caption(self, css_selector='td:nth-child(4)', alias="Email")
        self.active_start_date = element.Link(self, css_selector='td:nth-child(5)', alias="Active Start Date Text")
        self.active_end_date = element.Link(self, css_selector='td:nth-child(6)', alias="Active End Date Text")


class AdminSupervisorListItem(container.Container):
    alias = "Admin Supervisor List Item"
    css_selector = '#result_list > tbody > tr'
    element_as_source = True

    def controls_setup(self):
        """Admin Supervisor List Item controls"""

        self.supervisor_name = element.Link(self, css_selector='th:nth-child(1) > a',
                                            alias="Admin Supervisor Name Link")
        self.username = element.Caption(self, css_selector='td:nth-child(2)', alias="Username")
        self.email = element.Caption(self, css_selector='td:nth-child(3)', alias="Email")
        self.active_start_date = element.Link(self, css_selector='td:nth-child(4)', alias="Active Start Date Text")
        self.active_end_date = element.Link(self, css_selector='td:nth-child(5)', alias="Active End Date Text")


class AdminFormTools(container.Container):
    alias = "Admin Form Tools"
    css_selector = 'ul.menu-box'
    element_as_source = True

    def controls_setup(self):
        """Admin Client List Item controls"""

        self.history = element.Link(self, css_selector='li:nth-child(1) > a', alias="Item History")
        self.add = element.Link(self, css_selector='li:nth-child(2) > a', alias="Add Item")


class DashboardNavMenu(container.DashboardNavMenu):
    alias = 'Cormack Dashboard Nav Menu'


class DashboardJobMenu(container.Container):
    alias = "Dashboard Job Menu"

    def controls_setup(self):
        """Dashboard Job controls"""

        self.list = element.Link(self, alias="Manage Jobs", angular=True,
                                 css_selector='.dashboard-menu:nth-child(1) .list-group > a:nth-of-type(1)')
        self.slab = element.Link(self, alias="Slab Schedule", angular=True,
                                 css_selector='.dashboard-menu:nth-child(1) .list-group > a:nth-of-type(2)')
        self.new = element.Link(self, alias="Add New Job", angular=True,
                                css_selector='.dashboard-menu:nth-child(1) .list-group > a:nth-of-type(3)')


class DashboardRepairMenu(container.Container):
    alias = "Dashboard Repair Menu"

    def controls_setup(self):
        """Dashboard Repair controls"""

        self.list = element.Link(self, alias="Manage Repairs", angular=True,
                                 css_selector='.dashboard-menu:nth-child(2) .list-group > a:nth-of-type(1)')
        self.new = element.Link(self, alias="Add New Repair", angular=True,
                                css_selector='.dashboard-menu:nth-child(2) .list-group > a:nth-of-type(2)')


#   class DashboardReportMenu(container.Container):
#       alias = 'Dashboard Report Menu'

#       def controls_setup(self):
#           """Dashboard Report controls"""

#           self.library = element.Link(self, alias="Reports Library", angular=True,
#                                       css_selector='.dashboard-menu:nth-child(2) .list-group > a:nth-of-type(1)')


class JobListItem(container.Container):
    alias = "Job List Item"
    css_selector = 'table.jobs > tbody > tr'
    element_as_source = True

    def controls_setup(self):
        """Client List Item controls"""

        self.date_received = element.Link(self, alias="Date Received",
                                          css_selector='td:nth-child(1) > a', angular=True)
        self.job_type = element.Caption(self, alias="Job Type", css_selector='td:nth-child(2)', angular=True)
        self.description = element.Caption(self, alias="Client Name", css_selector='td:nth-child(3)', angular=True)
        self.address = element.Caption(self, alias="Address", css_selector='td:nth-child(4)', angular=True)
        self.suburb = element.Caption(self, alias="Suburb", css_selector='td:nth-child(5)', angular=True)
        self.client = element.Caption(self, alias="Client", css_selector='td:nth-child(6)', angular=True)


class MonthPicker(container.Container):
    """Representing <ocom-month-picker> element"""

    alias = "Month Picker"
    element_as_source = True

    def controls_setup(self):
        """MonthPicker controls"""

        self.month_box = element.InputElement(self, alias="Month Box", css_selector='input.date', angular=True)
        self.set_today = element.Button(self, alias="Set Today Button", css_selector='button.today',
                                        button_type='button', angular=True)
        self.clear = element.Button(self, alias="Clear Button", css_selector='button.clear', button_type='button',
                                    angular=True)


class DatePicker(container.Container):
    """Representing <ocom-date-picker> element"""

    alias = "Date Picker"
    element_as_source = True

    def controls_setup(self):
        """DatePicker controls"""

        self.date_box = element.InputElement(self, alias="Date Box", css_selector='input.date', angular=True)
        self.set_today = element.Button(self, alias="Set Today Button", css_selector='button.today',
                                        button_type='button', angular=True)
        self.clear = element.Button(self, alias="Clear Button", css_selector='button.clear', button_type='button',
                                    angular=True)


class DateTimePicker(container.Container):
    """Representing <ocom-datetime-picker> element"""

    alias = "DateTime Picker"
    element_as_source = True

    def controls_setup(self):
        """DateTimePicker controls"""

        super(DateTimePicker, self).controls_setup()
        self.time_box = element.InputElement(self, alias="Time Box", css_selector='input.time', angular=True)


class OcomInputBase(container.Container):
    alias = "Ocom Input Base"
    element_as_source = True

    def controls_setup(self):
        self.label = element.Caption(self, alias="Ocom Input Label", css_selector='label', angular=True)
        # TODO: add error list


class OcomInputDatePicker(OcomInputBase):
    """Representing <ocom-input> element with datepicker"""

    alias = "Ocom Input with DatePicker"
    element_as_source = True

    def controls_setup(self):
        """OcomInputDatePicker controls"""

        super(OcomInputDatePicker, self).controls_setup()
        self.date = DatePicker(self, alias="Ocom Input Datepicker", css_selector='ocom-date-picker', angular=True)


class OcomInputDateTimePicker(OcomInputBase):
    """Representing <ocom-input> element with datetime picker"""

    alias = "Ocom Input with DatePicker"
    element_as_source = True

    def controls_setup(self):
        """OcomInputDateTimePicker controls"""

        super(OcomInputDateTimePicker, self).controls_setup()
        self.date_time = DatePicker(self, alias="Ocom Input DateTimepicker", css_selector='ocom-datetime-picker',
                                    angular=True)


class OcomInputTextBox(OcomInputBase):
    """Representing <ocom-input> element with textbox"""

    alias = "Ocom Input with TextBox"
    element_as_source = True

    def controls_setup(self):
        """OcomInputTextBox controls"""
        super(OcomInputTextBox, self).controls_setup()
        self.text_box = element.InputElement(self, alias="TextBox Entry", css_selector='input', angular=True)


class OcomInputTextArea(OcomInputBase):
    """Representing <ocom-input> element with textarea"""

    alias = "Ocom Input with TextBox"
    element_as_source = True

    def controls_setup(self):
        """OcomInputTextArea controls"""
        super(OcomInputTextArea, self).controls_setup()
        self.text_box = element.InputElement(self, alias="TextArea Entry", css_selector='textarea', angular=True)


class OcomInputNumberBox(OcomInputBase):
    """Representing <ocom-input> element with textbox (number)"""

    alias = "Ocom Input with TextBox (Number)"
    element_as_source = True

    def controls_setup(self):
        """OcomInputNumberBox controls"""
        super(OcomInputNumberBox, self).controls_setup()
        self.number_box = element.InputElement(self, alias="NumberBox Entry", css_selector='input', angular=True)


class OcomInputMoneyBox(OcomInputNumberBox):
    """Representing <ocom-input> element with textbox (money)"""

    alias = "Ocom Input with TextBox (Money)"
    element_as_source = True

    def controls_setup(self):
        """OcomInputNumberBox controls"""

        super(OcomInputMoneyBox, self).controls_setup()
        self.currency = element.Caption(self, alias="Currency Label", css_selector='.input-group-addon', angular=True)


class OcomInputSelectBox(OcomInputBase):
    """Representing <ocom-input> element with select box"""

    alias = "Ocom Input with Select Box"
    element_as_source = True

    def controls_setup(self):
        """OcomInputSelectBox controls"""

        super(OcomInputSelectBox, self).controls_setup()
        self.select = element.InputElement(self, alias="SelectBox Entry", css_selector='select', angular=True)


class OcomInputCheckBox(OcomInputBase):
    """Representing <ocom-input> element with check box"""

    alias = "Ocom Input with Check Box"
    element_as_source = True

    def controls_setup(self):
        """OcomInputCheckBox controls"""

        super(OcomInputCheckBox, self).controls_setup()
        self.check_box = element.InputElement(self, alias="CheckBox Entry", css_selector='input', angular=True)
        self.symbol = element.Caption(self, alias="CheckBox Symbol", css_selector='.ocom-checkbox', angular=True)
