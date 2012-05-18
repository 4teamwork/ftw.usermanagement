from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.group.group_delete import GroupDelete
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class DeleteGroupTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(DeleteGroupTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_no_id(self):

        self.expect(self.gtool.removeGroups(ANY)).result(True)

        self.replay()

        GroupDelete(self.context, self.request).delete()

    def test_one_id(self):

        self.request['groupids'] = 'groupid'

        self.expect(self.gtool.removeGroups(ANY)).result(True)

        self.replay()

        GroupDelete(self.context, self.request).delete()

        self.assertEquals(self.message_cache.info, u'Group(s) deleted.')

    def test_more_ids(self):

        self.request['groupids'] = ['groupid_1', 'groupid_2']

        self.expect(self.gtool.removeGroups(ANY)).result(True)

        self.replay()

        GroupDelete(self.context, self.request).delete()

        self.assertEquals(self.message_cache.info, u'Group(s) deleted.')

    def test_bad_group_id(self):

        self.request['groupids'] = ['badid', 'groupid_2']

        self.expect(self.gtool.removeGroups(ANY)).throw(KeyError)

        self.replay()

        GroupDelete(self.context, self.request).delete()

        self.assertEquals(
            self.message_cache.error,
            u'There was an error while deleting a group.')
