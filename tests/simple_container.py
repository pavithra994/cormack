"""tests.simple_container.py - Container for Page object model in non-Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from ocom.tests import simple_container, simple_element as element


class TopNavbar(simple_container.Container):
    """Representing navigational bar group of buttons and search form"""

    alias = 'Top Navigation Bar'

    def controls_setup(self):
        """Top Navigation Bar controls"""
        self.login = element.Link(self, redirect_to='/accounts/signin/', alias='Navbar->Login Link')
        self.logout = element.Link(self, redirect_to='/accounts/signout/', alias='Navbar->Logout Link')


class LandingPageContent(simple_container.Container):
    """Representing Landing Page Content"""

    alias = 'Landing Page Content'

    def controls_setup(self):
        """Landing Page Content controls"""

        self.client = element.Link(self, redirect_to='/admin/api/client/',
                                   alias='Landing Page->Client Change Link')
        self.client_add = element.Link(self, redirect_to='/admin/api/client/add/', alias='Client Add Link')
        self.drain_type = element.Link(self, redirect_to='/admin/api/codedraintype/',
                                       alias='Landing Page->Code Drain Type Change Link')
        self.drain_type_add = element.Link(self, redirect_to='/admin/api/codedraintype/add/',
                                           alias='Landing Page->Code Drain Type Add Link')
        self.file_type = element.Link(self, redirect_to='/admin/api/codefiletype/',
                                      alias='Landing Page->Code File Type Change Link')
        self.file_type_add = element.Link(self, redirect_to='/admin/api/codefiletype/add/',
                                          alias='Landing Page->Code File Type Add Link')
        self.job_type = element.Link(self, redirect_to='/admin/api/codejobtype/',
                                     alias='Landing Page->Code Job Type Change Link')
        self.job_type_add = element.Link(self, redirect_to='/admin/api/codejobtype/add/',
                                         alias='Landing Page->Code Job Type Add Link')
        self.paving_colour = element.Link(self, redirect_to='/admin/api/codepavingcolour/',
                                          alias='Landing Page->Code Paving Colour Change Link')
        self.paving_colour_add = element.Link(self, redirect_to='/admin/api/codejobtype/add/',
                                              alias='Landing Page->Code Paving Colour Add Link')
        self.paving_type = element.Link(self, redirect_to='/admin/api/codepavingtype/',
                                        alias='Landing Page->Code Paving Type Change Link')
        self.paving_type_add = element.Link(self, redirect_to='/admin/api/codepavingtype/add/',
                                            alias='Landing Page->Code Paving Type Add Link')
        self.repair_type = element.Link(self, redirect_to='/admin/api/coderepairtype/',
                                        alias='Landing Page->Code Repair Type Change Link')
        self.repair_type_add = element.Link(self, redirect_to='/admin/api/coderepairtype/add/',
                                            alias='Landing Page->Code Repair Type Add Link')
        self.subbie_type = element.Link(self, redirect_to='/admin/api/codesubbietype/',
                                        alias='Landing Page->Code Subbie Type Change Link')
        self.subbie_type_add = element.Link(self, redirect_to='/admin/api/codesubbietype/add/',
                                            alias='Landing Page->Code Subbie Type Add Link')
        self.subbie = element.Link(self, redirect_to='/admin/api/subbie/', alias='Landing Page->Subbie Change Link')
        self.subbie_add = element.Link(self, redirect_to='/admin/api/subbie/add/',
                                       alias='Landing Page->Subbie Add Link')
        self.supervisor = element.Link(self, redirect_to='/admin/api/supervisor/',
                                       alias='Landing Page->Supervisor Change Link')
        self.supervisor_add = element.Link(self, redirect_to='/admin/api/supervisor/add/',
                                           alias='Landing Page->Supervisor Add Link'),
        self.task_type = element.Link(self, redirect_to='/admin/api/codetasktype/',
                                      alias='Landing Page->Code Task Type Change Link')
        self.task_type_add = element.Link(self, redirect_to='/admin/api/codetasktype/add/',
                                          alias='Landing Page->Code Task Type Add Link'),
