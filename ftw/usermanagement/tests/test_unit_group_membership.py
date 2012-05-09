# coding=UTF-8
from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.group.group_membership import GroupMembership
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class DisplayUsersTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(DisplayUsersTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.group_membership = self.mocker.patch(
            GroupMembership(self.context, self.request))
        self.expect(self.group_membership.get_users(ANY)).call(lambda x: x)

        self.member_1 = self.mocker.mock(count=False)
        self.expect(
            self.member_1.getProperty('fullname', ANY)).result('Jämes Bond')
        self.expect(self.member_1.getUserId()).result('member_1')

        self.member_2 = self.mocker.mock(count=False)
        self.expect(
            self.member_2.getProperty('fullname', ANY)).result('')
        self.expect(self.member_2.getUserId()).result('member_2')

    def test_no_users(self):

        msearch = self.mocker.replace(
            'ftw.usermanagement.browser.utils.membership_search')
        self.expect(msearch(ANY, searchGroups=ANY)).result([])

        self.replay()

        result = self.group_membership.get_display_users([])

        self.assertEquals(result, [])

    def test_with_current_users(self):

        msearch = self.mocker.replace(
            'ftw.usermanagement.browser.utils.membership_search')
        self.expect(msearch(ANY, searchGroups=ANY)).result(
            [self.member_1, self.member_2])

        self.replay()

        result = self.group_membership.get_display_users(['member_2'])

        self.assertEquals(
            result,
            [{
                'userid': 'member_1',
                'name': 'Jämes Bond',
                'is_member_of': False,
            },
            {
                'userid': 'member_2',
                'name': 'member_2',
                'is_member_of': True,
            }],
        )

    def test_no_current_users(self):

        msearch = self.mocker.replace(
            'ftw.usermanagement.browser.utils.membership_search')
        self.expect(msearch(ANY, searchGroups=ANY)).result(
            [self.member_1, self.member_2])

        self.replay()

        result = self.group_membership.get_display_users([])

        self.assertEquals(
            result,
            [{
                'userid': 'member_1',
                'name': 'Jämes Bond',
                'is_member_of': False,
            },
            {
                'userid': 'member_2',
                'name': 'member_2',
                'is_member_of': False,
            }],
        )


class ReplaceGroupMembersTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ReplaceGroupMembersTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

        self.group_membership = self.mocker.patch(
            GroupMembership(self.context, self.request))
        self.expect(self.group_membership.get_users(ANY)).call(lambda x: x)

        self.removed_users = []
        self.added_users = []

        self.expect(self.gtool.removePrincipalFromGroup(
            ANY, ANY, ANY)).call(lambda x, y, z: self.removed_users.append(x))
        self.expect(self.gtool.addPrincipalToGroup(
            ANY, ANY, ANY)).call(lambda x, y, z: self.added_users.append(x))

    def test_nothing(self):

        self.replay()

        result = self.group_membership.replace_group_members([], [])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_users) == 0)
        self.assertTrue(len(self.added_users) == 0)

    def test_add(self):

        self.replay()

        result = self.group_membership.replace_group_members(
            [], ['user1', 'user2'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_users) == 0)
        self.assertTrue(len(self.added_users) == 2)

    def test_remove(self):

        self.replay()

        result = self.group_membership.replace_group_members(
            ['user1', 'user2'], [])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_users) == 2)
        self.assertTrue(len(self.added_users) == 0)

    def test_remove_and_add(self):

        self.replay()

        result = self.group_membership.replace_group_members(
            ['user1', 'user2'], ['user3', 'user4'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_users) == 2)
        self.assertTrue(len(self.added_users) == 2)

    def test_leave_all(self):

        self.replay()

        result = self.group_membership.replace_group_members(
            ['user1', 'user2'], ['user1', 'user2'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_users) == 0)
        self.assertTrue(len(self.added_users) == 0)


class CallTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(CallTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

    def test_no_group_id(self):

        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({})

        self.replay()

        result = GroupMembership(self.context, request)()

        self.assertEquals(result, 'No group selected')

    def test_form_submitted(self):

        self.request['group_id'] = "Group_1"
        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({'form.submitted': True})

        group_membership = self.mocker.patch(
            GroupMembership(self.context, request))
        self.expect(
            group_membership.replace_group_members(ANY, ANY)).result('replace')

        self.replay()

        result = group_membership()

        self.assertEquals(result, 'replace')

    def test_form_not_submitted(self):

        self.request['group_id'] = "Group_1"
        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({'form.submitted': False})

        group_membership = self.mocker.patch(
            GroupMembership(self.context, request))
        self.expect(
            group_membership.render(ANY)).result('render')

        self.replay()

        result = group_membership()

        self.assertEquals(result, 'render')


class GetUsersTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(GetUsersTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')

        self.member_1 = self.mocker.mock(count=False)
        self.expect(
            self.member_1.getProperty('fullname', ANY)).result('Jämes Bond')

        self.member_2 = self.mocker.mock(count=False)
        self.expect(
            self.member_2.getProperty('fullname', ANY)).result('')

    def test_no_members(self):

        self.expect(self.gtool.getGroupMembers(ANY)).result([])

        self.replay()

        gm = GroupMembership(self.context, self.request)
        result = gm.get_users('no_group')

        # No users
        self.assertEquals(result, [])

    def test_with_members(self):

        self.expect(self.gtool.getGroupMembers(ANY)).result(
            ['fullname', 'no_fullname', 'admin'])

        # No member, just id
        self.expect(self.mtool.getMemberById('admin')).result(None)

        # Member with fullname
        self.expect(
            self.mtool.getMemberById('fullname')).result(self.member_1)

        # Member without fullname
        self.expect(self.mtool.getMemberById(
            'no_fullname')).result(self.member_2)

        self.replay()

        gm = GroupMembership(self.context, self.request)
        result = gm.get_users('group_id')

        # Sorted list with userids
        self.assertEquals(result, ['fullname', 'admin', 'no_fullname'])
