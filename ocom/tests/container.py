"""tests.container.py - Container for Page object model in Selenium tests"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from . import app, element, wait


class Container(app.BaseItem):
    """General container with bound controls"""

    item_type = 'Container'

    def __init__(self, test_object, **kwargs):
        """Container initialization method

        :param tests.page.SeleniumPage test_object: the source test object
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        super(Container, self).__init__(test_object, **kwargs)
        self.controls_setup()

    # noinspection PyMethodMayBeStatic
    def controls_setup(self):
        """Override this on inheriting classes"""

        raise NotImplemented("Override this function by adding elements")


# Deprecated
class Alert(Container):
    """Representing an alert message"""

    alias = 'Alert Message'
    css_selector = '.alert'
    element_as_source = True

    def __init__(self, test_object, message_type='', **kwargs):
        """Container initialization method

        :param tests.page.SeleniumPage test_object: the source test object
        :param str message_type: the message type. possible values are 'error', 'success', 'warning'
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        self.message_type = message_type
        super(Alert, self).__init__(test_object, **kwargs)

    def controls_setup(self):
        """Alert message controls"""

        self.view_cart = element.Link(self, alias='View Cart Link', css_selector='.alertinner a.cart')
        self.checkout = element.Link(self, alias='Checkout Now Link', css_selector='.alertinner a.checkout')
        self.total = element.Caption(self, alias='Cart Total', css_selector='.alertinner .price_color')
        self.close = element.LinkButton(self, alias='Message Close Button', css_selector='a.close')


class AdminDashboardFooter(Container):
    alias = 'Admin Dashboard Footer'
    css_selector = 'div.footer > .content'
    element_as_source = True

    def controls_setup(self):
        """Footer controls"""

        self.ocomsoft_link = element.Link(self, alias='Ocom Software Link', css_selector='.tools > a')
        self.footer_title = element.Caption(self, alias='Branding (Footer)', css_selector='.branding')
        self.version = element.Caption(self, alias='Software Version', css_selector='.copyright')


class DashboardNavMenu(Container):
    alias = 'Dashboard Nav Menu'
    css_selector = 'nav.navbar > .container'
    element_as_source = True

    def controls_setup(self):
        """Nav Menu controls"""

        self.site = element.Link(self, alias='Site Link', css_selector='a#navbar-brand', angular=True)
        self.account_dropdown = element.Link(self, alias='Account Dropdown', css_selector='ul.nav > li.dropdown > a',
                                             angular=True)
        self.account_profile = element.Link(self, alias='Account Profile', dom_id='account_profile', angular=True)
        self.admin_dashboard = element.Link(self, alias='Admin Dashboard', dom_id='admin_dashboard', angular=True)
        self.logout = element.Link(self, alias='Account Logout', dom_id='account_logout', angular=True)


class AdminDashboardNavMenu(Container):
    alias = 'Admin Dashboard Nav Menu'
    css_selector = '#header'
    element_as_source = True

    def controls_setup(self):
        """Nav Menu controls"""

        self.site = element.Link(self, alias='Site Link', css_selector='#branding > a')
        self.change_password = element.Link(self, alias='Change Password Link',
                                            css_selector='.user-links a:nth-of-type(1)')
        self.logout = element.Link(self, alias='Logout Link', css_selector='.user-links a:nth-of-type(2)')


class AdminDashboardLeftSidebar(Container):
    alias = 'Admin Dashboard Left Sidebar'
    css_selector = '#suit-left'

    def controls_setup(self):
        """Submodule controls"""

        self.login = element.Link(self, alias='Submodule Change Link',
                                  css_selector='#left-nav > ul > li:nth-child(1) a')
        self.main = element.Link(self, alias='Back to Main Dashboard',
                                 css_selector='#left-nav > ul > li:nth-child(2) a')


class AdminDashboardSubmodule(Container):
    alias = 'Admin Dashboard Submodule'
    css_selector = 'tbody'
    element_as_source = True

    def controls_setup(self):
        """Submodule controls"""

        self.title = element.Caption(self, alias='Submodule Title', css_selector=':nth-child(1)')
        self.change = element.Link(self, alias='Submodule Change Link', css_selector=':nth-child(2) > a')
        self.add = element.Link(self, alias='Submodule Add Link', css_selector=':nth-child(3) > a')


class StaticImageContainer(Container):
    """Representing static image container on homepage"""

    alias = 'Static Image Section'
    css_selector = '#home_static_image'
    element_as_source = True

    def controls_setup(self):
        """Static Image container"""

        self.image = element.ImageLink(self, alias='Static Image', css_selector='img.featured')
        self.image_link = element.ImageLink(self, alias='Static Image (Link)', css_selector='a')
        self.heading = element.Caption(self, alias='Main Heading', css_selector='.heading > .main-text')
        self.subheading = element.Caption(self, alias='SubHeading', css_selector='.heading > .sub-text')


class DropdownLinks(Container):
    """Representing dynamic dropdown group of links"""

    alias = 'Navigation Links'
    css_selector = 'ul.dropdown-menu > li'
    element_as_source = True

    def controls_setup(self):
        """Dropdown link controls"""

        self.link = element.Link(self, css_selector='a', alias='Dropdown Nav Link')


class TopNavbar(Container):
    """Representing navigational bar group of buttons and search form"""

    alias = 'Top Navigation Bar'
    css_selector = '#desktop-interaction'
    element_as_source = True

    def controls_setup(self):
        """Top Navigation Bar controls"""

        self.login = element.Link(self, class_name='nav-login', alias='Navbar->Login Link')
        self.register = element.Link(self, class_name='nav-register', alias='Navbar->Register Link')
        self.logout = element.Link(self, class_name='nav-logout', alias='Navbar->Logout Link')
        self.be_a_merchant = element.Link(self, class_name='nav-partner-join',
                                          alias='Navbar->Be A Merchant Link')
        self.wishlist = element.Link(self, class_name='nav-wishlist', alias='Navbar->Wishlist Icon Button')
        self.cart = element.Link(self, class_name='nav-cart', alias='Navbar->Cart Icon Button')
        self.account = element.Link(self, css_selector='a.nav-account', alias='Navbar->Account Link')
        self.messages = element.Link(self, class_name='nav-messages', alias='Navbar->Messages Link')
        self.dashboard = element.Link(self, class_name='nav-dashboard', alias='Navbar->Dashboard Link')
        self.messages_count = element.Element(self, dom_id='postman_unread_count',
                                              alias='Navbar->Unread Messages Count Label')

        self.search_query = element.TextBox(self, name='q', alias='Navbar->Search Box')
        self.search_button = element.Button(self, css_selector='form.search button[type=submit]',
                                            alias='Navbar->Search Icon Button')


class MobileNavbar(TopNavbar):
    """Representing navigational bar group of buttons and search form in mobile mode"""

    alias = 'Nav Menu (Mobile)'
    css_selector = '#mobile-interaction'
    element_as_source = True

    def controls_setup(self):
        """MobileNavbar controls"""

        self.login = element.Link(self, class_name='nav-login', alias='Navbar->Login Link')
        self.register = element.Link(self, class_name='nav-register', alias='Navbar->Register Link')
        self.logout = element.Link(self, class_name='nav-logout', alias='Navbar->Logout Link')
        self.be_a_merchant = element.Link(self, class_name='nav-partner-join',
                                          alias='Navbar->Be A Merchant Link')
        self.wishlist = element.Link(self, class_name='nav-wishlist', alias='Navbar->Wishlist Icon Button')
        self.cart = element.Link(self, class_name='nav-cart', alias='Navbar->Cart Icon Button')
        self.account = element.Link(self, css_selector='a.nav-account', alias='Navbar->Account Link')
        self.messages = element.Link(self, class_name='nav-messages', alias='Navbar->Messages Link')
        self.dashboard = element.Link(self, class_name='nav-dashboard', alias='Navbar->Dashboard Link')
        self.messages_count = element.Element(self, dom_id='postman_unread_count',
                                              alias='Navbar->Unread Messages Count Label')

        self.search_query = element.TextBox(self, name='q', alias='Navbar->Search Box')
        self.search_button = element.Button(self, css_selector='form.search button[type=submit]',
                                            alias='Navbar->Search Icon Button')


class CategoriesNavbar(Container):
    """Categories Navigation bar"""

    alias = 'Categories Menu Bar'
    css_selector = '.navbar.primary .action-background'
    menu_css_selector = '#browse > li'

    def __init__(self, test_object, fixed=True, **kwargs):
        """Categories navbar initialization method

        :param tests.page.SeleniumPage test_object: the source test object
        :param bool fixed: if True, categories are fixed; otherwise, use dynamic TopMenuLink list
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        self.fixed = fixed
        super(CategoriesNavbar, self).__init__(test_object, **kwargs)

    def controls_setup(self):
        """Standard Menu Navbar (refer to tests/codeship/catalogue.json)"""

        self.new_items = element.TopMenuLink(self, alias='New Items Menu',
                                             css_selector='#browse > li:nth-child(1) > a')
        if self.fixed:
            self.jewelry = element.TopMenuLink(self, alias='Jewelry Menu',
                                               css_selector='#browse > li:nth-child(2) > a')
            self.artwork = element.TopMenuLink(self, alias='Artwork Menu',
                                               css_selector='#browse > li:nth-child(3) > a')
            self.homeware = element.TopMenuLink(self, alias='Homeware Menu',
                                                css_selector='#browse > li:nth-child(4) > a')
            self.clothing = element.TopMenuLink(self, alias='Clothing Menu',
                                                css_selector='#browse > li:nth-child(5) > a')
            self.vintage = element.TopMenuLink(self, alias='Vintage Menu',
                                               css_selector='#browse > li:nth-child(6) > a')
            self.food = element.TopMenuLink(self, alias='Food Menu',
                                            css_selector='#browse > li:nth-child(7) > a')
            self.rings = element.SubMenuLink(self, alias='Jewelry->Rings Submenu',
                                             css_selector='#browse > li:nth-child(2) > ul > li:nth-child(1) > a')
            self.necklaces = element.SubMenuLink(self, alias='Jewelry->Necklaces Submenu',
                                                 css_selector='#browse > li:nth-child(2) > ul > li:nth-child(2) > a')
            self.bracelets = element.SubMenuLink(self, alias='Jewelry->Bracelets Submenu',
                                                 css_selector='#browse > li:nth-child(2) > ul > li:nth-child(3) > a')
            self.earrings = element.SubMenuLink(self, alias='Jewelry->Earrings Submenu',
                                                css_selector='#browse > li:nth-child(2) > ul > li:nth-child(4) > a')
            self.broaches = element.SubMenuLink(self, alias='Jewelry->Broaches and Pins Submenu',
                                                css_selector='#browse > li:nth-child(2) > ul > li:nth-child(5) > a')
            self.wall_art = element.SubMenuLink(self, alias='Artwork->Wall Art Submenu',
                                                css_selector='#browse > li:nth-child(3) > ul > li:nth-child(1) > a')
            self.ceramics = element.SubMenuLink(self, alias='Jewelry->Ceramics Submenu',
                                                css_selector='#browse > li:nth-child(3) > ul > li:nth-child(2) > a')
            self.sculpture = element.SubMenuLink(self, alias='Jewelry->Sculpture Submenu',
                                                 css_selector='#browse > li:nth-child(3) > ul > li:nth-child(3) > a')
            self.living = element.SubMenuLink(self, alias='Homeware->Living Submenu',
                                              css_selector='#browse > li:nth-child(4) > ul > li:nth-child(1) > a')
            self.furniture = element.SubMenuLink(self, alias='Homeware->Furniture Submenu',
                                                 css_selector='#browse > li:nth-child(4) > ul > li:nth-child(2) > a')
            self.kitchen = element.SubMenuLink(self, alias='Homeware->Kitchen Submenu',
                                               css_selector='#browse > li:nth-child(4) > ul > li:nth-child(3) > a')
            self.lighting = element.SubMenuLink(self, alias='Homeware->Lighting Submenu',
                                                css_selector='#browse > li:nth-child(4) > ul > li:nth-child(4) > a')
            self.outdoor = element.SubMenuLink(self, alias='Homeware->Outdoor Submenu',
                                               css_selector='#browse > li:nth-child(4) > ul > li:nth-child(5) > a')
            self.organize = element.SubMenuLink(self, alias='Homeware->Organize Submenu',
                                                css_selector='#browse > li:nth-child(4) > ul > li:nth-child(6) > a')
            self.party = element.SubMenuLink(self, alias='Homeware->Party Submenu',
                                             css_selector='#browse > li:nth-child(4) > ul > li:nth-child(7) > a')
            self.sub_food = element.SubMenuLink(self, alias='Homeware->Food Submenu',
                                                css_selector='#browse > li:nth-child(4) > ul > li:nth-child(8) > a')
            self.pets = element.SubMenuLink(self, alias='Homeware->For Pets Submenu',
                                            css_selector='#browse > li:nth-child(4) > ul > li:nth-child(9) > a')
            self.women = element.SubMenuLink(self, alias='Clothing->Women Submenu',
                                             css_selector='#browse > li:nth-child(5) > ul > li:nth-child(1) > a')
            self.men = element.SubMenuLink(self, alias='Clothing->Men Submenu',
                                           css_selector='#browse > li:nth-child(5) > ul > li:nth-child(2) > a')
            self.kids = element.SubMenuLink(self, alias='Clothing->Kids Submenu',
                                            css_selector='#browse > li:nth-child(5) > ul > li:nth-child(3) > a')
            self.pet_lovers = element.SubMenuLink(self, alias='Clothing->Pet Lovers Submenu',
                                                  css_selector='#browse > li:nth-child(5) > ul > li:nth-child(4) > a')
            self.antiques = element.SubMenuLink(self, alias='Vintage->Antiques Submenu',
                                                css_selector='#browse > li:nth-child(6) > ul > li:nth-child(1) > a')
            self.accessories = element.SubMenuLink(self, alias='Vintage->Accessories Submenu',
                                                   css_selector='#browse > li:nth-child(6) > ul > li:nth-child(2) > a')
            self.sub_clothing = element.SubMenuLink(self, alias='Vintage->Clothing Submenu',
                                                    css_selector='#browse > li:nth-child(6) > ul > li:nth-child(3) > a')
            self.sub_homeware = element.SubMenuLink(self, alias='Vintage->Homeware Submenu',
                                                    css_selector='#browse > li:nth-child(6) > ul > li:nth-child(4) > a')
            self.toys = element.SubMenuLink(self, alias='Vintage->Toys Submenu',
                                            css_selector='#browse > li:nth-child(6) > ul > li:nth-child(5) > a')
            self.books = element.SubMenuLink(self, alias='Vintage->Books Submenu',
                                             css_selector='#browse > li:nth-child(6) > ul > li:nth-child(6) > a')
        else:
            self.menus = []


class CatalogueSidebar(Container):
    """Representing sidebar group of buttons for Catalogue and Search"""

    alias = 'Catalogue Sidebar'
    css_selector = '#sidebar_categories'
    element_as_source = True

    def controls_setup(self):
        """Catalogue Sidebar controls"""

        self.recently_added = element.Link(self, alias="Recently Added Menu",
                                           css_selector='ul.nav li:nth-child(1) > a')
        self.all_items = element.Link(self, alias="All Items Menu",
                                      css_selector='ul.nav li:nth-child(2) > a')
        self.jewelry = element.TopMenuLink(self, alias='Jewelry Menu',
                                           css_selector='ul.nav li:nth-child(3) > a')
        self.jewelry_active = element.Caption(self, alias='Jewelry Menu',
                                              css_selector='ul.nav li:nth-child(3) > span.selected')
        self.artwork = element.TopMenuLink(self, alias='Artwork Menu',
                                           css_selector='ul.nav li:nth-child(4) > a')
        self.homeware = element.TopMenuLink(self, alias='Homeware Menu',
                                            css_selector='ul.nav li:nth-child(5) > a')
        self.clothing = element.TopMenuLink(self, alias='Clothing Menu',
                                            css_selector='ul.nav li:nth-child(6) > a')
        self.vintage = element.TopMenuLink(self, alias='Vintage Menu',
                                           css_selector='ul.nav li:nth-child(7) > a')
        self.food = element.TopMenuLink(self, alias='Food Menu',
                                        css_selector='ul.nav li:nth-child(8) > a')
        self.rings = element.SubMenuLink(self, alias='Jewelry->Rings Submenu',
                                         css_selector='ul.nav li:nth-child(3) > ul > li:nth-child(1) > a')
        self.necklaces = element.SubMenuLink(self, alias='Jewelry->Necklaces Submenu',
                                             css_selector='ul.nav li:nth-child(3) > ul > li:nth-child(2) > a')
        self.bracelets = element.SubMenuLink(self, alias='Jewelry->Bracelets Submenu',
                                             css_selector='ul.nav li:nth-child(3) > ul > li:nth-child(3) > a')
        self.earrings = element.SubMenuLink(self, alias='Jewelry->Earrings Submenu',
                                            css_selector='ul.nav li:nth-child(3) > ul > li:nth-child(4) > a')
        self.broaches = element.SubMenuLink(self, alias='Jewelry->Broaches and Pins Submenu',
                                            css_selector='ul.nav li:nth-child(3) > ul > li:nth-child(5) > a')
        self.wall_art = element.SubMenuLink(self, alias='Artwork->Wall Art Submenu',
                                            css_selector='ul.nav li:nth-child(4) > ul > li:nth-child(1) > a')
        self.ceramics = element.SubMenuLink(self, alias='Jewelry->Ceramics Submenu',
                                            css_selector='ul.nav li:nth-child(4) > ul > li:nth-child(2) > a')
        self.sculpture = element.SubMenuLink(self, alias='Jewelry->Sculpture Submenu',
                                             css_selector='ul.nav li:nth-child(4) > ul > li:nth-child(3) > a')
        self.living = element.SubMenuLink(self, alias='Homeware->Living Submenu',
                                          css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(1) > a')
        self.furniture = element.SubMenuLink(self, alias='Homeware->Furniture Submenu',
                                             css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(2) > a')
        self.kitchen = element.SubMenuLink(self, alias='Homeware->Kitchen Submenu',
                                           css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(3) > a')
        self.lighting = element.SubMenuLink(self, alias='Homeware->Lighting Submenu',
                                            css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(4) > a')
        self.outdoor = element.SubMenuLink(self, alias='Homeware->Outdoor Submenu',
                                           css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(5) > a')
        self.organize = element.SubMenuLink(self, alias='Homeware->Organize Submenu',
                                            css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(6) > a')
        self.party = element.SubMenuLink(self, alias='Homeware->Party Submenu',
                                         css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(7) > a')
        self.sub_food = element.SubMenuLink(self, alias='Homeware->Food Submenu',
                                            css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(8) > a')
        self.pets = element.SubMenuLink(self, alias='Homeware->For Pets Submenu',
                                        css_selector='ul.nav li:nth-child(5) > ul > li:nth-child(9) > a')
        self.women = element.SubMenuLink(self, alias='Clothing->Women Submenu',
                                         css_selector='ul.nav li:nth-child(6) > ul > li:nth-child(1) > a')
        self.men = element.SubMenuLink(self, alias='Clothing->Men Submenu',
                                       css_selector='ul.nav li:nth-child(6) > ul > li:nth-child(2) > a')
        self.kids = element.SubMenuLink(self, alias='Clothing->Kids Submenu',
                                        css_selector='ul.nav li:nth-child(6) > ul > li:nth-child(3) > a')
        self.pet_lovers = element.SubMenuLink(self, alias='Clothing->Pet Lovers Submenu',
                                              css_selector='ul.nav li:nth-child(6) > ul > li:nth-child(4) > a')
        self.antiques = element.SubMenuLink(self, alias='Vintage->Antiques Submenu',
                                            css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(1) > a')
        self.accessories = element.SubMenuLink(self, alias='Vintage->Accessories Submenu',
                                               css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(2) > a')
        self.sub_clothing = element.SubMenuLink(self, alias='Vintage->Clothing Submenu',
                                                css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(3) > a')
        self.sub_homeware = element.SubMenuLink(self, alias='Vintage->Homeware Submenu',
                                                css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(4) > a')
        self.toys = element.SubMenuLink(self, alias='Vintage->Toys Submenu',
                                        css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(5) > a')
        self.books = element.SubMenuLink(self, alias='Vintage->Books Submenu',
                                         css_selector='ul.nav li:nth-child(7) > ul > li:nth-child(6) > a')


class ProductTypeSidebar(Container):
    """Representing sidebar for Product Types"""

    alias = 'Product Type Sidebar'
    css_selector = 'dl.type'

    def controls_setup(self):
        """Product Type Sidebar controls"""
        pass


class RatingSidebar(Container):
    """Representing sidebar for Product Ratings"""

    alias = 'Rating Sidebar'
    # TODO: get CSS selector
    css_selector = 'TODO'

    def controls_setup(self):
        """Ratings Sidebar controls"""
        pass


class ProfileSidebar(Container):
    """Representing sidebar group of buttons for Account Profile"""

    alias = 'Profile Sidebar'
    css_selector = 'ul.profile.nav-list'

    def controls_setup(self):
        """Profile Sidebar controls"""

        self.profile = element.Link(self, class_name='sidebar-profile', alias='Sidebar->Profile Link')
        self.order = element.Link(self, class_name='sidebar-order', alias='Sidebar->Orders Link')
        self.sell = element.Link(self, class_name='sidebar-sell', alias='Sidebar->Sell a Product Link')
        self.be_a_merchant = element.Link(self, class_name='sidebar-merchant', alias='Sidebar->Be A Merchant Link')
        self.address = element.Link(self, class_name='sidebar-address', alias='Sidebar->Address Book Link')
        self.email = element.Link(self, class_name='sidebar-email', alias='Sidebar->E-mails Link')
        self.alerts = element.Link(self, class_name='sidebar-alerts', alias='Sidebar->Alerts Link')
        self.notifications = element.Link(self, class_name='sidebar-notifications', alias='Sidebar->Notifications Link')
        self.wishlist = element.Link(self, class_name='sidebar-wishlist', alias='Sidebar->Wishlists Link')


class FooterFirstColumn(Container):
    """Standard Page Leftmost Footer"""

    alias = 'First Column Footer'
    css_selector = 'footer ul.first li'
    element_as_source = True

    def controls_setup(self):
        """Footer link controls"""

        self.link = element.Link(self, css_selector='a', alias='Footer Link')


class FooterSecondColumn(Container):
    """Standard Page Middle Footer"""

    alias = 'Second Column Footer'
    css_selector = 'footer ul.second li'
    element_as_source = True

    def controls_setup(self):
        """Footer link controls"""

        self.link = element.Link(self, css_selector='a', alias='Footer Link')


class MessagesNavigationBar(Container):
    """Core Messages Navigation Bar"""

    alias = 'Messages Nav Bar'
    css_selector = '#messaging_container + .content'

    def controls_setup(self):
        """Messages Navigation Bar controls"""

        self.inbox = element.NavigationTab(self, css_selector='.messaging a.nav-inbox', alias='Inbox Tab')
        self.sent = element.NavigationTab(self, css_selector='.messaging a.nav-sent', alias='Sent Tab')
        self.write = element.NavigationTab(self, css_selector='.messaging a.nav-write', alias='Write Tab')
        self.archives = element.NavigationTab(self, css_selector='.messaging a.nav-archive', alias='Archives Tab')
        self.trash = element.NavigationTab(self, css_selector='.messaging a.nav-trash', alias='Trash Tab')


class SentMessageRow(Container):
    """SentMessage Row (for messaging)"""

    css_selector = '#pm_messages tbody tr'
    alias = 'Sent Message Row'
    element_as_source = True
    is_sender = True

    def __init__(self, test_object, **kwargs):
        """Container initialization method

        :param tests.page.SeleniumPage test_object: the source test object
        :param str alias: the descriptive name of the item
        :param str class_name: the item class name
        :param str css_selector: the CSS selector of the item
        :param str dom_id: the item DOM ID
        :param str name: the item DOM name
        :param str xpath: the item xpath
        """

        super(SentMessageRow, self).__init__(test_object, **kwargs)

    def controls_setup(self):
        """Message Row controls"""

        self.item_select = element.CheckBox(self, alias="Select Checkbox",
                                            css_selector='td:nth-child(1) > input[type=checkbox]')

        if self.is_sender:
            self.recipient = element.Caption(self, alias="Recipient", css_selector='td:nth-child(2)')
        else:
            self.sender = element.Caption(self, alias="Sender", css_selector='td:nth-child(2)')

        self.message_link = element.Link(self, alias="Message Link", css_selector='td:nth-child(3) a')
        self.time = element.Caption(self, alias="Time Sent", css_selector='td:nth-child(4)')


class ReceivedMessageRow(SentMessageRow):
    """Received Message Row"""

    alias = 'Inbox Message Row'
    is_sender = False


class MailingListPopup(Container):
    """Mailing List sliding popup"""

    alias = 'Mailing List Popup'
    css_selector = '.mailing-list-confirm'

    def controls_setup(self):
        """Mailing List Popup controls"""

        self.email = element.TextBox(self, dom_id='mailing-list-email', alias='E-mail Textbox')
        self.close = element.Button(self, button_type='button', css_selector='.mailing-list-confirm .btn-close',
                                    alias='Close Button')
        self.signup = element.Button(self, css_selector='form.slide-left button[type=submit]', alias='Subscribe Button')

    def wait_until_slide(self, message='', timeout=None, update=True, tabs=0):
        """
        Wait for popup to finish sliding by detecting class property change

        :param str message: the message to display before looking for the element
        :param float timeout: the number of seconds to expire before timeout
        :param bool update: if True, runs update reference first
        :param int tabs: the number of tabs to use as indentation
        """

        if update:
            self._update_reference(tabs=tabs)

        self.utils.start_timer('item_wait_slide', self.timers)

        if timeout is None:
            timeout = wait.PAGE_TIMEOUT

        self.utils.console("Waiting for {} {} to slide...".format(self.item_type, self.name)
                           if message == '' else message, tabs=tabs)
        self._wait_until_css_selector_is_present('{}.animation-done'.format(self.css_selector), timeout)
        self.utils.time_elapsed('item_wait_slide', self.timers, tabs=tabs + 1)


class DashboardTopNavbar(Container):
    """Dashboard Top Navigation Bar"""

    alias = 'Dashboard Top Navigation Bar'
    css_selector = '.dashboard .nav-accounts'

    def controls_setup(self):
        """Dashboard Top Navigation bar controls"""

        self.to_homepage = element.Link(self, class_name='nav-home', alias='Return to site Link')
        self.account = element.Link(self, class_name='nav-account', alias='Account Profile Link')
        self.logout = element.Link(self, class_name='nav-logout', alias='Logout Link')


class TopMenu(Container):
    """Top Menu"""

    menu_type = 'highlight-dropdown'
    """:param str menu_type: Type of Menu (possible values are: 'highlight-dropdown', 'click-dropdown', 'link')"""


class DashboardMenuBar(Container):
    """Dashboard Menu Bar"""

    alias = 'Dashboard Menu Bar'
    css_selector = '.dashboard ul.top-main'

    def controls_setup(self):
        """Dashboard Menu Bar controls"""
        self.dashboard = element.Link(self, class_name='menu-dashboard', alias='Dashboard Menu')
        # catalogue and sub-menus
        self.catalogue = element.LinkButton(self, class_name='menu-catalogue', alias='Catalogue Menu')
        self.products = element.Link(self, class_name='submenu-products', alias='Catalogue->Products Menu')
        self.product_types = element.Link(self, class_name='submenu-product-types',
                                          alias='Catalogue->Product Types Menu')
        self.categories = element.Link(self, class_name='submenu-categories', alias='Catalogue->Categories Menu')
        self.ranges = element.Link(self, class_name='submenu-ranges', alias='Catalogue->Ranges Menu')
        self.stock_alerts = element.Link(self, class_name='submenu-low-stock-alerts',
                                         alias='Catalogue->Low Stock Alerts Menu')
        # fulfilment and sub-menus
        self.fulfilment = element.LinkButton(self, class_name='menu-fulfilment', alias='Fulfilment Menu')
        self.orders = element.Link(self, class_name='submenu-orders', alias='Fulfilment->Orders Menu')
        self.statistics = element.Link(self, class_name='submenu-statistics', alias='Fulfilment->Statistics Menu')
        self.partners = element.Link(self, class_name='submenu-partners', alias='Fulfilment->Partners Menu')
        # customers and sub-menus
        self.customers = element.LinkButton(self, class_name='menu-customers', alias='Customers Menu')
        self.customers_submenu = element.Link(self, class_name='submenu-customers', alias='Customers->Customers Menu')
        self.deleted_accounts = element.Link(self, class_name='submenu-deleted_accounts',
                                             alias='Customers->Deleted Accounts Menu')
        self.stock_alert_requests = element.Link(self, class_name='submenu-stock-alert-requests-customers',
                                                 alias='Customers->Stock Alert Requests Menu')
        # offers and sub-menus
        self.offers = element.LinkButton(self, class_name='menu-offers', alias='Offers Menu')
        self.offers_submenu = element.Link(self, class_name='submenu-offers', alias='Offers->Offers Menu')
        self.vouchers = element.Link(self, class_name='submenu-vouchers', alias='Offers->Vouchers Menu')
        # content and sub-menus
        self.content_menu = element.LinkButton(self, class_name='menu-content', alias='Content Menu')
        self.pages = element.Link(self, class_name='menu-pages', alias='Content->Pages Menu')
        self.announcements = element.Link(self, class_name='menu-announcements', alias='Content->Announcements Menu')
        self.reviews = element.Link(self, class_name='menu-reviews', alias='Content->Reviews Menu')

        self.reports = element.Link(self, class_name='menu-reports', alias='Reports Menu')
        self.store_info = element.LinkButton(self, css_selector='.dropdown.store > a', alias='Store Info Menu')
        self.partner_store = []
