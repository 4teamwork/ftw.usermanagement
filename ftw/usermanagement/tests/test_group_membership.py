from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
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
