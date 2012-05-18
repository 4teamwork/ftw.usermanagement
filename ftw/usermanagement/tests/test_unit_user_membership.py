# coding=UTF-8
from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.user_membership import UserMembership
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class DisplayGroupsTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(DisplayGroupsTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.user_membership = self.mocker.patch(
            UserMembership(self.context, self.request))
        self.expect(self.user_membership.get_groups(ANY)).call(lambda x: x)

        self.group_1 = self.mocker.mock(count=False)
        self.expect(self.group_1.getId()).result('group_1')
        self.expect(self.group_1.getGroupTitleOrName()).result('Groüp 1')

        self.group_2 = self.mocker.mock(count=False)
        self.expect(self.group_2.getId()).result('group_2')
        self.expect(self.group_2.getGroupTitleOrName()).result('Group 2')

        self.group_3 = self.mocker.mock(count=False)
        self.expect(self.group_3.getId()).result('AuthenticatedUsers')
        self.expect(self.group_3.getGroupTitleOrName()).result('Group 2')

    def test_no_groups(self):

        self.expect(
            self.user_membership.membershipSearch(searchUsers=ANY)).result([])

        self.replay()

        result = self.user_membership.get_display_groups([])

        self.assertEquals(result, [])

    def test_with_current_groups(self):

        self.expect(
            self.user_membership.membershipSearch(searchUsers=ANY)).result(
                [self.group_1, self.group_2])

        self.replay()

        result = self.user_membership.get_display_groups(['group_2'])

        self.assertEquals(
            result,
            [{
                'name': 'group_1',
                'title': 'Groüp 1',
                'is_member_of': False,
            },
            {
                'name': 'group_2',
                'title': 'Group 2',
                'is_member_of': True,
            }],
        )

    def test_no_current_groups(self):

        self.expect(
            self.user_membership.membershipSearch(searchUsers=ANY)).result(
                [self.group_1, self.group_2])

        self.replay()

        result = self.user_membership.get_display_groups([])

        self.assertEquals(
            result,
            [{
                'name': 'group_1',
                'title': 'Groüp 1',
                'is_member_of': False,
            },
            {
                'name': 'group_2',
                'title': 'Group 2',
                'is_member_of': False,
            }],
        )

    def test_authenthicated_group(self):

        self.expect(
            self.user_membership.membershipSearch(searchUsers=ANY)).result(
                [self.group_3])

        self.replay()

        result = self.user_membership.get_display_groups([])

        self.assertEquals(result, [])


class ReplaceGroupTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ReplaceGroupTests, self).setUp()

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

        self.user_membership = self.mocker.patch(
            UserMembership(self.context, self.request))
        self.expect(self.user_membership.get_groups(ANY)).call(lambda x: x)

        self.removed_groups = []
        self.added_groups = []

        self.expect(self.gtool.removePrincipalFromGroup(
            ANY, ANY, ANY)).call(lambda x, y, z: self.removed_groups.append(x))
        self.expect(self.gtool.addPrincipalToGroup(
            ANY, ANY, ANY)).call(lambda x, y, z: self.added_groups.append(x))

    def test_nothing(self):

        self.replay()

        result = self.user_membership.replace_groups([], [])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 0)
        self.assertTrue(len(self.added_groups) == 0)

    def test_add(self):

        self.replay()

        result = self.user_membership.replace_groups(
            [], ['group1', 'group2'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 0)
        self.assertTrue(len(self.added_groups) == 2)

    def test_remove(self):

        self.replay()

        result = self.user_membership.replace_groups(
            ['group1', 'group2'], [])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 2)
        self.assertTrue(len(self.added_groups) == 0)

    def test_remove_and_add(self):

        self.replay()

        result = self.user_membership.replace_groups(
            ['group1', 'group2'], ['user3', 'user4'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 2)
        self.assertTrue(len(self.added_groups) == 2)

    def test_leave_all(self):

        self.replay()

        result = self.user_membership.replace_groups(
            ['group1', 'group2'], ['group1', 'group2'])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 0)
        self.assertTrue(len(self.added_groups) == 0)

    def test_authenthicated_group(self):

        self.replay()

        result = self.user_membership.replace_groups(
            ['AuthenticatedUsers'], [])

        self.assertEquals(result, True)
        self.assertEquals(self.message_cache.info, u'Changes made.')
        self.assertTrue(len(self.removed_groups) == 0)
        self.assertTrue(len(self.added_groups) == 0)


class CallTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(CallTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

    def test_no_user_id(self):

        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({})

        self.replay()

        result = UserMembership(self.context, request)()

        self.assertEquals(result, 'No user selected')

    def test_form_submitted(self):

        self.request['userid'] = "User_1"
        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({'form.submitted': True})

        user_membership = self.mocker.patch(
            UserMembership(self.context, request))
        self.expect(
            user_membership.replace_groups(ANY, ANY)).result('replace')

        self.replay()

        result = user_membership()

        self.assertEquals(result, 'replace')

    def test_form_not_submitted(self):

        self.request['userid'] = "User_1"
        request = self.mocker.proxy(self.request)
        self.expect(request.form).result({'form.submitted': False})

        user_membership = self.mocker.patch(
            UserMembership(self.context, request))
        self.expect(
            user_membership.render(ANY)).result('render')

        self.replay()

        result = user_membership()

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
        self.expect(self.mtool.getMemberById(ANY)).call(lambda x: x)

        self.group_1 = self.mocker.mock(count=False)
        self.expect(self.group_1.getGroupTitleOrName()).result('member group')
        self.expect(self.group_1.getId()).result('group_1')

        self.group_2 = self.mocker.mock(count=False)
        self.expect(self.group_2.getGroupTitleOrName()).result('admin group')
        self.expect(self.group_2.getId()).result('group_2')

        self.group_3 = self.mocker.mock(count=False)
        self.expect(self.group_3.getGroupTitleOrName()).result('user group')
        self.expect(self.group_3.getId()).result('group_3')

    def test_no_groups(self):

        self.expect(self.gtool.getGroupsForPrincipal(ANY)).result([])

        self.replay()

        um = UserMembership(self.context, self.request)
        result = um.get_groups('no_group')

        # No users
        self.assertEquals(result, [])

    def test_with_members(self):

        self.expect(self.gtool.getGroupsForPrincipal(ANY)).result(
            ['member_group', 'admin_group', 'user_group'])

        self.expect(
            self.gtool.getGroupById('member_group')).result(self.group_1)
        self.expect(
            self.gtool.getGroupById('admin_group')).result(self.group_2)
        self.expect(
            self.gtool.getGroupById('user_group')).result(self.group_3)

        self.replay()

        um = UserMembership(self.context, self.request)
        result = um.get_groups('group_id')

        # Sorted list with userids
        self.assertEquals(result, ['group_2', 'group_1', 'group_3'])
