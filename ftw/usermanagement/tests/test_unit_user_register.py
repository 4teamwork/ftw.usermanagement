from ftw.testing import MockTestCase
from ftw.usermanagement.browser.user.user_register import UserRegister
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from mocker import ANY
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class ValidateTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ValidateTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')

        self.site_root = self.mocker.mock(count=False)
        self.mock_utility(self.site_root, ISiteRoot)
        self.expect(self.site_root.getId()).result('portal_id')

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = []
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: self.message_cache.append({type: msg}))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_no_errors(self):

        self.expect(self.rtool.isMemberIdAllowed(ANY)).result(True)
        self.expect(self.rtool.isValidEmail(ANY)).result(True)

        self.replay()

        data = {
            'email': 'valid_email',
            'firstname': 'valid_firstname',
            'lastname': 'valid_lastname',
            'username': 'valid_username',
            }

        result = UserRegister(
            self.context, self.request).validate_registration(data)

        self.assertEquals(result, True)

    def test_empty_firstname_lastname_email(self):

        self.expect(self.rtool.isMemberIdAllowed(ANY)).result(True)
        self.expect(self.rtool.isValidEmail(ANY)).result(True)

        self.replay()

        data = {
            'email': '',
            'firstname': '',
            'lastname': '',
            }

        result = UserRegister(
            self.context, self.request).validate_registration(data)

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache) == 3)
        self.assertTrue(
            self.message_cache[0], {'error': u'text_missing_firstname'})
        self.assertTrue(
            self.message_cache[1], {'error': u'text_missing_lastname'})
        self.assertTrue(
            self.message_cache[2], {'error': u'text_missing_email'})

    def test_reserved_username(self):

        self.expect(self.rtool.isMemberIdAllowed(ANY)).result(True)
        self.expect(self.rtool.isValidEmail(ANY)).result(True)

        self.replay()

        data = {
            'email': 'valid_email',
            'firstname': 'valid_firstname',
            'lastname': 'valid_lastname',
            'username': 'portal_id',
        }

        result = UserRegister(
            self.context, self.request).validate_registration(data)

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache) == 1)
        self.assertTrue(
            self.message_cache[0],
            {'error': "This username is reserved. Please "
            "choose a different name."})

    def test_invalid_username(self):

        self.expect(self.rtool.isMemberIdAllowed(ANY)).result(False)
        self.expect(self.rtool.isValidEmail(ANY)).result(True)

        self.replay()

        data = {
            'email': 'valid_email',
            'firstname': 'valid_firstname',
            'lastname': 'valid_lastname',
            'username': 'invalid_username',
        }

        result = UserRegister(
            self.context, self.request).validate_registration(data)

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache) == 1)
        self.assertTrue(
            self.message_cache[0],
            {'error': u"The login name you selected is already"
            "in use or is not valid. Please choose another."})

    def test_invalid_email(self):

        self.expect(self.rtool.isMemberIdAllowed(ANY)).result(True)
        self.expect(self.rtool.isValidEmail(ANY)).result(False)

        self.replay()

        data = {
            'email': 'invalid_email',
            'firstname': 'valid_firstname',
            'lastname': 'valid_lastname',
            'username': 'valid_username',
        }

        result = UserRegister(
            self.context, self.request).validate_registration(data)

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache) == 1)
        self.assertTrue(
            self.message_cache[0],
            {'error': u'You must enter a valid email address.'})


class RegisterTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(RegisterTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')
        self.expect(self.mtool.memberareaCreationFlag(ANY)).result(True)
        self.expect(self.mtool.createMemberarea(ANY)).result(True)

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')
        self.expect(self.rtool.getPassword(length=8)).result('12345678')
        self.expect(self.rtool.addMember(
            'attribute_error',
            ANY,
            properties=ANY,
            REQUEST=ANY)).throw(AttributeError)
        self.expect(self.rtool.addMember(
            'value_error',
            ANY,
            properties=ANY,
            REQUEST=ANY)).throw(ValueError)
        self.expect(self.rtool.addMember(
            'ok',
            ANY,
            properties=ANY,
            REQUEST=ANY)).result(True)

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_ok(self):

        self.request['email'] = 'ok'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, True)
        self.assertEquals(
            self.message_cache.__dict__.get('info'), u'User added.')

    def test_value_error(self):

        self.request['email'] = 'value_error'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertEquals(
            type(self.message_cache.__dict__.get('error')), ValueError)

    def test_attribute_error(self):

        self.request['email'] = 'attribute_error'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertEquals(
            type(self.message_cache.__dict__.get('error')), AttributeError)

    def test_validation_error(self):

        self.request['email'] = 'ok'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(False)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache.__dict__) == 0)
