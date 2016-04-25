from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.usermanagement.tests import FunctionalTestCase
from operator import attrgetter


class TestGroupMembership(FunctionalTestCase):

    @browsing
    def test_group_membership_assignment(self, browser):
        self.grant('Manager')

        create(Builder('user')
               .named('Captain', 'Hindsight'))

        create(Builder('user')
               .named('Chief', 'Wiggum')
               .in_groups('Administrators'))

        browser.login().open(view='tabbedview_view-groups_management')
        browser.click_on('Administrators')
        self.assertEquals(
            ['Wiggum Chief'],
            browser.css('select[name="new_users:list"] option[selected]').text)

        browser.fill({'new_users:list': ['chief.wiggum',
                                         'captain.hindsight']}).submit()

        browser.open(view='tabbedview_view-groups_management')
        browser.click_on('Administrators')
        self.assertEquals(
            ['Hindsight Captain', 'Wiggum Chief'],
            browser.css('select[name="new_users:list"] option[selected]').text)

    @browsing
    def test_user_manager_is_not_enough_to_manage_admin_groups(self, browser):
        """A "User Manager" should not be able to assign himself or other users
        to groups which have admin roles such as "Manager" or
        "Site Administrators", because the user manager whould be able to get
        hold of more previliges.
        """

        self.grant('User Manager')
        browser.login().open(view='tabbedview_view-groups_management')
        browser.click_on('Administrators')
        self.assertFalse(browser.css('form'))
        statusmessages.assert_message('For modifying the membership of this'
                                      ' group you require the roles: Manager.')

    @browsing
    def test_user_manager_can_edit_non_admin_roles(self, browser):
        self.grant('User Manager')
        browser.login().open(view='tabbedview_view-groups_management')
        browser.click_on('Reviewers')
        self.assertTrue(browser.css('form'))
