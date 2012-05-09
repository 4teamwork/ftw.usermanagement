from ftw.testing import MockTestCase
from mocker import ANY, KWARGS
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.user_delete import UserDelete
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class DeleteUserTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(DeleteUserTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')
        self.expect(self.mtool.deleteMembers(ANY, KWARGS)).result(True)

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_no_id(self):

        self.replay()

        UserDelete(self.context, self.request).delete()

        self.assertEquals(self.message_cache.info, u'text_user_deleted')

    def test_one_id(self):

        self.request['userids'] = 'userid'

        self.replay()

        UserDelete(self.context, self.request).delete()

        self.assertEquals(self.message_cache.info, u'text_user_deleted')

    def test_more_ids(self):

        self.request['userids'] = ['userid_1', 'userid_1']

        self.replay()

        UserDelete(self.context, self.request).delete()

        self.assertEquals(self.message_cache.info, u'text_user_deleted')
