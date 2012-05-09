from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.user_register import UserRegister
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class UserTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(UserTests, self).setUp()

        self.request = {}

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')
        self.expect(self.mtool.memberareaCreationFlag(ANY)).result(True)
        self.expect(self.mtool.createMemberarea(ANY)).result(True)

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')
        self.expect(self.rtool.generatePassword()).result('12345')
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

    def test_register_ok(self):

        self.request['email'] = 'ok'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, True)
        self.assertEquals(
            self.message_cache.__dict__.get('info'), u'User added.')

    def test_register_value_error(self):

        self.request['email'] = 'value_error'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertEquals(
            type(self.message_cache.__dict__.get('error')), ValueError)


    def test_register_attribute_error(self):

        self.request['email'] = 'attribute_error'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(True)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertEquals(
            type(self.message_cache.__dict__.get('error')), AttributeError)

    def test_register_validation_error(self):

        self.request['email'] = 'ok'

        register_obj = self.mocker.patch(
            UserRegister(self.context, self.request))

        self.expect(register_obj.validate_registration(ANY)).result(False)

        self.replay()

        result = register_obj.register()

        self.assertEquals(result, False)
        self.assertTrue(len(self.message_cache.__dict__) == 0)
