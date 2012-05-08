from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.group.groups import GroupsSearchResultExecutor
from plone.app.controlpanel.interfaces import IPloneControlPanelView
from zope.interface import Interface


class GroupTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(GroupTests, self).setUp()

        self.request = self.stub_request()

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

    def base_get_groups(self, query, result):

        groups = [
            {'groupid': 'group1', 'title': 'Group1'},
            {'groupid': 'group111', 'title': 'Group111'},
            {'groupid': 'group11', 'title': 'Group11'},
            {'groupid': 'group3', 'title': 'Group3'},
            {'groupid': 'AuthenticatedUsers', 'title': 'Auth'},
            {'groupid': 'group2', 'title': 'Group2'},
        ]

        groupprefs = self.mocker.mock(count=False)
        self.mock_adapter(
            groupprefs,
            IPloneControlPanelView,
            (Interface, Interface),
            name=u'usergroup-groupprefs',
        )
        self.expect(groupprefs(ANY, ANY)).result(groupprefs)

        self.expect(groupprefs.doSearch(searchString=ANY)).result(groups)

        self.replay()

        executor = GroupsSearchResultExecutor(self.context, query)

        self.assertEquals(executor.get_results(), result)

    def test_get_groups_no_filter(self):

        query = {'filter_text': ''}

        result = [
            {'group_id': 'group1', 'group_title': 'Group1'},
            {'group_id': 'group11', 'group_title': 'Group11'},
            {'group_id': 'group111', 'group_title': 'Group111'},
            {'group_id': 'group2', 'group_title': 'Group2'},
            {'group_id': 'group3', 'group_title': 'Group3'},
        ]

        self.base_get_groups(query, result)

    def test_get_groups_with_filter(self):

        query = {'filter_text': 'Group1'}

        result = [
            {'group_id': 'group1', 'group_title': 'Group1'},
            {'group_id': 'group11', 'group_title': 'Group11'},
            {'group_id': 'group111', 'group_title': 'Group111'},
        ]

        self.base_get_groups(query, result)
