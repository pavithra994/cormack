#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import simple_page, simple_element
from . import simple_container as container


class DashboardPage(simple_page.DashboardPage):
    def form_setup(self):
        self.content_links = container.LandingPageContent(self)


class SigninPage(simple_page.SigninPage):
    pass


class SignoutPage(simple_page.SignoutPage):
    pass


class ClientPage(simple_page.StandardPage):
    alias = "Dashboard: Client Page"
    url_path = '/admin/api/client/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/client/add/',
                                            alias="Dashboard: Client Add Link")


class ClientAddPage(simple_page.StandardPage):
    alias = "Dashboard: Client Add Page"
    url_path = '/admin/api/client/add/'


class DrainTypePage(simple_page.StandardPage):
    alias = "Dashboard: Drain Type Page"
    url_path = '/admin/api/codedraintype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codedraintype/add/',
                                            alias="Dashboard: Drain Type Add Link")


class DrainTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Drain Type Add Page"
    url_path = '/admin/api/codedraintype/add/'


class FileTypePage(simple_page.StandardPage):
    alias = "Dashboard: File Type Page"
    url_path = '/admin/api/codefiletype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codefiletype/add/',
                                            alias="Dashboard: File Type Add Link")


class FileTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: File Type Add Page"
    url_path = '/admin/api/codefiletype/add/'


class JobTypePage(simple_page.StandardPage):
    alias = "Dashboard: Job Type Page"
    url_path = '/admin/api/codejobtype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codejobtype/add/',
                                            alias="Dashboard: Job Type Add Link")


class JobTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Job Type Add Page"
    url_path = '/admin/api/codejobtype/add/'


class PavingColourPage(simple_page.StandardPage):
    alias = "Dashboard: Paving Coluur Page"
    url_path = '/admin/api/codepavingcolour/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codepavingcolour/add/',
                                            alias="Dashboard: Paving Colour Add Link")


class PavingColourAddPage(simple_page.StandardPage):
    alias = "Dashboard: Paving Colour Add Page"
    url_path = '/admin/api/codepavingcolour/add/'


class PavingTypePage(simple_page.StandardPage):
    alias = "Dashboard: Paving Type Page"
    url_path = '/admin/api/codepavingtype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codepavingtype/add/',
                                            alias="Dashboard: Paving Type Add Link")


class PavingTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Paving Type Add Page"
    url_path = '/admin/api/codepavingtype/add/'


class RepairTypePage(simple_page.StandardPage):
    alias = "Dashboard: Repair Type Page"
    url_path = '/admin/api/coderepairtype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/coderepairtype/add/',
                                            alias="Dashboard: Repair Type Add Link")


class RepairTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Repair Type Add Page"
    url_path = '/admin/api/coderepairtype/add/'


class SubbieTypePage(simple_page.StandardPage):
    alias = "Dashboard: Subbie Type Page"
    url_path = '/admin/api/codesubbietype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codesubbietype/add/',
                                            alias="Dashboard: Subbie Type Add Link")


class SubbieTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Subbie Type Add Page"
    url_path = '/admin/api/codesubbietype/add/'


class TaskTypePage(simple_page.StandardPage):
    alias = "Dashboard: Task Type Page"
    url_path = '/admin/api/codetasktype/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/codetasktype/add/',
                                            alias="Dashboard: Task Type Add Link")


class TaskTypeAddPage(simple_page.StandardPage):
    alias = "Dashboard: Task Type Add Page"
    url_path = '/admin/api/codetasktype/add/'


class SubbiePage(simple_page.StandardPage):
    alias = "Dashboard: Subbie Page"
    url_path = '/admin/api/subbie/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/subbie/add/',
                                            alias="Dashboard: Subbie Add Link")


class SubbieAddPage(simple_page.StandardPage):
    alias = "Dashboard: Subbie Add Page"
    url_path = '/admin/api/subbie/add/'


class SupervisorPage(simple_page.StandardPage):
    alias = "Dashboard: Supervisor Page"
    url_path = '/admin/api/supervisor/'

    def form_setup(self):
        self.add_link = simple_element.Link(self, redirect_to='/admin/api/supervisor/add/',
                                            alias="Dashboard: Supervisor Add Link")


class SupervisorAddPage(simple_page.StandardPage):
    alias = "Dashboard: Supervisor Add Page"
    url_path = '/admin/api/supervisor/add/'
