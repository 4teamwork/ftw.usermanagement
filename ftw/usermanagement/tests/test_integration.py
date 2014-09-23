# coding=UTF-8
from ftw.usermanagement.browser.group.group_add import GroupAdd
from ftw.usermanagement.browser.group.group_delete import GroupDelete
from ftw.usermanagement.browser.group.group_membership import GroupMembership
from ftw.usermanagement.browser.user.user_delete import UserDelete
from ftw.usermanagement.browser.user.user_membership import UserMembership
from ftw.usermanagement.browser.user.user_register import UserRegister
from ftw.usermanagement.interfaces import IFtwUserManagement
from ftw.usermanagement.testing import USERMANAGEMENT_PLONE_LAYER
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.interface import directlyProvidedBy, directlyProvides
import re


class MemberIntegrationTests(TestCase):

    layer = USERMANAGEMENT_PLONE_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.mtool = getToolByName(self.portal, 'portal_membership')
        self.acl = getToolByName(self.portal, 'acl_users')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Layer for request
        ifaces = [IFtwUserManagement] + list(directlyProvidedBy(self.request))
        directlyProvides(self.request, *ifaces)

        # Set authenticator flag to get a valid request
        value = self.portal.restrictedTraverse(
            '@@authenticator').authenticator()
        auth = re.search('value="(.*)"', value).group(1)
        self.request.form = dict(_authenticator=auth)
        self.request.other['method'] = 'POST'

        # Setup 10 Users
        registration = getToolByName(self.portal, 'portal_registration')
        for i in range(10):
            registration.addMember(
                'user_%s@test.ch' % i,
                '12345',
                properties={
                    'username': 'user_%s' % i,
                    'email': 'user_%s@test.ch' % i,
                    },
                REQUEST=self.layer['request'])

        # Setup 5 Groups
        groups_tool = getToolByName(self.portal, 'portal_groups')
        for i in range(5):
            groups_tool.addGroup('group_%s' % i)

    def test_add_user_with_homefolder(self):
        # Setup Members Folder
        self.mtool.setMemberareaCreationFlag()
        self.portal.invokeFactory('Folder',id='Members')

        self.request['firstname'] = 'Jämes'
        self.request['lastname'] = 'Bönd'
        self.request['email'] = 'james@bond.ch'

        UserRegister(self.portal, self.request)()

        info = self.mtool.getMemberInfo('james@bond.ch')

        self.assertEquals(info.get('fullname'), 'Bönd Jämes')

        self.assertTrue(self.mtool.getHomeFolder('james@bond.ch'))

    def test_add_group(self):

        self.request['group_id'] = 'test_group'
        self.request['group_title'] = 'Test Gröup'

        GroupAdd(self.portal, self.request)()

        self.assertNotEquals(self.acl.getGroupById('test_group'), None)

    def test_delete_user(self):

        member_1 = self.mtool.getMemberById('user_1@test.ch')
        member_2 = self.mtool.getMemberById('user_2@test.ch')

        self.assertNotEquals(member_1, None)
        self.assertNotEquals(member_2, None)

        self.request['userids'] = ['user_1@test.ch', 'user_2@test.ch']

        UserDelete(self.portal, self.request).delete()

        member_1 = self.mtool.getMemberById('user_1@test.ch')
        member_2 = self.mtool.getMemberById('user_2@test.ch')

        self.assertEquals(member_1, None)
        self.assertEquals(member_2, None)

    def test_delete_group(self):

        group_1 = self.acl.source_groups.getGroupById('group_1')
        group_2 = self.acl.source_groups.getGroupById('group_2')

        self.assertNotEquals(group_1, None)
        self.assertNotEquals(group_2, None)

        self.request['groupids'] = ['group_1', 'group_2']

        GroupDelete(self.portal, self.request).delete()

        group_1 = self.acl.source_groups.getGroupById('group_1')
        group_2 = self.acl.source_groups.getGroupById('group_2')

        self.assertEquals(group_1, None)
        self.assertEquals(group_2, None)

    def test_user_membership(self):

        groups = self.acl.getUserById('user_1@test.ch').getGroupIds()

        self.assertNotIn('group_1', groups)
        self.assertNotIn('group_2', groups)

        self.request['userid'] = 'user_1@test.ch'
        self.request.form.update({'form.submitted': True})
        self.request.form.update({'new_groups': ['group_1', 'group_2']})

        UserMembership(self.portal, self.request)()

        groups = self.acl.getUserById('user_1@test.ch').getGroupIds()

        self.assertIn('group_1', groups)
        self.assertIn('group_2', groups)

    def test_group_membership(self):

        members = self.acl.getGroupById('group_1').getGroupMemberIds()

        self.assertNotIn('user_1@test.ch', members)
        self.assertNotIn('user_2@test.ch', members)

        self.request['group_id'] = 'group_1'
        self.request.form.update({'form.submitted': True})
        self.request.form.update(
            {'new_users': ['user_1@test.ch', 'user_2@test.ch']})

        GroupMembership(self.portal, self.request)()

        members = self.acl.getGroupById('group_1').getGroupMemberIds()

        self.assertIn('user_1@test.ch', members)
        self.assertIn('user_2@test.ch', members)

    def test_user_overview(self):

        view = self.portal.restrictedTraverse(
            '@@tabbedview_view-users_management')()

        # Check for any users in the view
        self.assertIn('user_1@test.ch', view)
        self.assertIn('user_9@test.ch', view)

    def test_group_overview(self):

        view = self.portal.restrictedTraverse(
            '@@tabbedview_view-groups_management')()

        # Check for any groups in the view
        self.assertIn('group_1', view)
        self.assertIn('group_4', view)

    def test_tabbed_management(self):

        view = self.portal.restrictedTraverse('user_management')()

        # Check tabs
        self.assertIn('users_management', view)
        self.assertIn('groups_management', view)
