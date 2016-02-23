# coding=UTF-8
from ftw.testing import MockTestCase
from mocker import ANY, KWARGS
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.user_notify import UserNotify
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface
from Products.CMFCore.interfaces import IPropertiesTool


class GetOptionsTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(GetOptionsTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))
        self.expect(
            self.notify.reset_password(ANY)).result('12345').count(0, None)

        self.member = self.mocker.mock(count=False)
        self.expect(self.member.getProperty('email')).result('james@bond.ch')
        self.expect(
            self.member.getProperty('fullname', ANY)).result('James Bond')
        self.expect(self.member.id).result('user_id_1')

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')
        self.expect(self.mtool.getHomeFolder(ANY)).result(self.context)
        self.expect(self.context.absolute_url()).result('http://nowhere/')
        self.expect(self.mtool.absolute_url()).result('http://nowhere/')

        self.urltool = self.mocker.mock(count=False)
        self.mock_tool(self.urltool, 'portal_url')
        self.expect(self.urltool()).result('http://nohost/plone')
        self.expect(
            self.urltool.getPortalObject().Title()).result('Pörtal Title')

        self.ptool = self.mocker.mock(count=False)
        self.mock_utility(self.ptool, IPropertiesTool)
        self.expect(self.ptool.email_from_address).result('contact@test.ch')

    def test_no_member(self):

        self.expect(self.mtool.getMemberById(ANY)).result(None)

        self.replay()

        result = self.notify.get_options('user_id', False)

        self.assertEquals(result, False)

    def test_with_member_no_pw_reset(self):

        self.expect(self.mtool.getMemberById(ANY)).result(self.member)

        self.replay()

        result = self.notify.get_options('user_id', False)

        self.assertEquals(result['email'], 'james@bond.ch')
        self.assertEquals(result['username'], 'user_id_1')
        self.assertEquals(result['fullname'], 'James Bond')
        self.assertEquals(result['site_title'], 'Pörtal Title')
        self.assertEquals(result['contact_email'], 'contact@test.ch')
        self.assertEquals(result['pw'], None)
        self.assertEquals(result['reset_pw'], False)
        self.assertEquals(result['pw_reset_url'], 'http://nohost/plone/@@change-password')

    def test_with_member_and_pw_reset(self):

        self.expect(self.mtool.getMemberById(ANY)).result(self.member)

        self.replay()

        result = self.notify.get_options('user_id', True)

        self.assertEquals(result['email'], 'james@bond.ch')
        self.assertEquals(result['username'], 'user_id_1')
        self.assertEquals(result['fullname'], 'James Bond')
        self.assertEquals(result['site_title'], 'Pörtal Title')
        self.assertEquals(result['contact_email'], 'contact@test.ch')
        self.assertEquals(result['pw'], '12345')
        self.assertEquals(result['reset_pw'], True)
        self.assertEquals(result['pw_reset_url'], 'http://nohost/plone/@@change-password')


class ResetPasswordTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ResetPasswordTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))

        self.rolemaker = self.mocker.mock()
        self.expect(self.rolemaker.getRolesForPrincipal(ANY)).result(['role'])

        self.plugins = [['plugin_id', self.rolemaker]]

        self.acl_user_folder = []
        self.acltool = self.mocker.mock(count=False)
        self.mock_tool(self.acltool, 'acl_users')
        self.expect(self.acltool.plugins.listPlugins(ANY)).result(self.plugins)
        self.expect(self.acltool.getUserById(ANY)).call(lambda x: x)
        self.expect(self.acltool.userFolderEditUser(
            ANY, ANY, ANY, ANY, KWARGS)).call(
                lambda x, y, z, a, REQUEST: self.acl_user_folder.append(
                    {'member': x, 'password': y, 'roles': z}))

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')
        self.expect(self.rtool.getPassword(length=8)).result('12345678')

        self.member = self.mocker.mock(count=False)
        self.expect(self.member.id).result('user_id_1')
        self.expect(self.member.getDomains()).result('domains')

    def test_reset_pw(self):

        self.replay()

        result = self.notify.reset_password(self.member)

        self.assertEquals(result, '12345678')
        self.assertEquals(len(self.acl_user_folder), 1)
        self.assertEquals(self.acl_user_folder[0]['member'], 'user_id_1')
        self.assertEquals(self.acl_user_folder[0]['password'], '12345678')
        self.assertEquals(self.acl_user_folder[0]['roles'], ['role'])


class GetMailObjectTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(GetMailObjectTests, self).setUp()

        self.notify_view = self.mocker.mock()
        self.expect(self.notify_view(KWARGS)).result(u'Body Täxt')

        self.request = {}
        self.context = self.stub()
        self.expect(
            self.context.unrestrictedTraverse(ANY)).result(self.notify_view)

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))

        self.urltool = self.mocker.mock(count=False)
        self.mock_tool(self.urltool, 'portal_url')
        self.expect(
            self.urltool.getPortalObject().Title()).result('Pörtal Title')

        self.ptool = self.mocker.mock(count=False)
        self.mock_utility(self.ptool, IPropertiesTool)
        self.expect(self.ptool.email_from_name).result('James Bönd')
        self.expect(self.ptool.email_from_address).result('james@bond.ch')

        self.options = {'email': 'ted@mos.ch'}

    def test_get_mail_object(self):

        self.replay()

        result = self.notify.get_mail_object(self.options)

        self.assertEquals(
            result._headers[0][1], 'multipart/alternative')
        self.assertEquals(
            result._headers[2][1]._chunks[0][0], 'Welcome on Pörtal Title')
        self.assertEquals(
            result._headers[3][1], 'James Bönd<james@bond.ch>')
        self.assertEquals(
            result._headers[4][1], 'ted@mos.ch')

class ValidateTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ValidateTests, self).setUp()

        self.mailhost = self.mocker.mock()

        self.request = {}
        self.context = self.stub()
        self.expect(
            self.context.unrestrictedTraverse(ANY)).result(self.mailhost)

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_valid(self):

        options = {
            'email': 'user_1',
        }

        self.expect(self.mailhost.mailhost_warning()).result(False)

        self.replay()

        result = self.notify.validate(options)

        self.assertEquals(result, True)

    def test_no_options(self):

        options = False

        self.replay()

        result = self.notify.validate(options)

        self.assertEquals(result, False)
        self.assertEquals(
            self.message_cache.error,
            u'There was an error to look up a user')

    def test_no_mailhost(self):

        options = {
            'email': 'user_1',
        }

        self.expect(self.mailhost.mailhost_warning()).result(True)

        self.replay()

        result = self.notify.validate(options)

        self.assertEquals(result, False)
        self.assertEquals(
            self.message_cache.error,
            u'No mailhost defined. contact site Administrator.')

    def test_no_email(self):

        options = {
            'email': '',
        }

        self.expect(self.mailhost.mailhost_warning()).result(False)

        self.replay()

        result = self.notify.validate(options)

        self.assertEquals(result, False)
        self.assertEquals(self.message_cache.error, u'no_email_for_user')

class SendNotificationTest(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(SendNotificationTest, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.hosttool = self.mocker.mock(count=False)
        self.mock_tool(self.hosttool, 'MailHost')
        self.expect(self.hosttool.send(ANY, mto=ANY)).result(True)

        self.options = {'fullname': 'Üser 1', 'email': 'mail_1'}

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))
        self.expect(self.notify.get_options(ANY, ANY)).result(self.options)

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_not_valid(self):

        self.expect(self.notify.validate(ANY)).result(False)

        self.replay()

        result = self.notify.send_user_notification('uid')

        self.assertEquals(result, False)

    def test_valid(self):

        self.expect(self.notify.validate(ANY)).result(True)
        self.expect(self.notify.get_mail_object(ANY)).result('mail')

        self.replay()

        self.notify.send_user_notification('uid')

        self.assertEquals(
            self.message_cache.info,
            u"text_usermanagament_user_notified",
        )


class CallTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(CallTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.notification_pool = []

        self.notify = self.mocker.patch(UserNotify(self.context, self.request))
        self.expect(self.notify.send_user_notification(ANY, ANY)).call(
            lambda x, y: self.notification_pool.append({x: y})).count(0, None)

    def test_no_userids(self):

        self.replay()

        self.notify()

        self.assertEquals(len(self.notification_pool), 0)

    def test_one_userid(self):

        self.request['userids'] = 'user_1'

        self.replay()

        self.notify()

        self.assertEquals(len(self.notification_pool), 1)
        self.assertEquals(self.notification_pool[0].get('user_1'), False)

    def test_more_userids(self):

        self.request['userids'] = ['user_1', 'user_2', 'user_3']

        self.replay()

        self.notify()

        self.assertEquals(len(self.notification_pool), 3)
        self.assertEquals(self.notification_pool[0].get('user_1'), False)
        self.assertEquals(self.notification_pool[1].get('user_2'), False)
        self.assertEquals(self.notification_pool[2].get('user_3'), False)

    def test_with_pw_reset(self):

        self.request['userids'] = ['user_1']
        self.request['reset_pw'] = True

        self.replay()

        self.notify()

        self.assertEquals(self.notification_pool[0].get('user_1'), True)
