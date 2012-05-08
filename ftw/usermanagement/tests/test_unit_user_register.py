from ftw.testing import MockTestCase
from mocker import ANY, KWARGS
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

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')

    def base_register(self, request, errors):

        self.expect(self.mtool.memberareaCreationFlag(ANY)).result(True)
        self.expect(self.mtool.createMemberarea(ANY)).result(True)

        statusmsg = self.mocker.mock(count=False)
        message_cache = self.create_dummy()
        self.expect(statusmsg(ANY).addStatusMessage(ANY, KWARGS)).call(
            lambda msg, type: setattr(message_cache, type, msg))
        self.mock_adapter(statusmsg, IStatusMessage, (Interface, ))

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

        register_obj = UserRegister(self.context, request)
        register = self.mocker.patch(register_obj)
        self.expect(register.validate_registration(ANY)).result(errors)

        self.replay()
        register()

        self.assertEquals(request.get('errors', []), errors)

        return message_cache

    def test_register_ok(self):

        message = self.base_register(Request({'email': 'ok'}), [])

        self.assertTrue(len(message.__dict__) == 1)
        self.assertEquals(message.__dict__.get('info'), u'User added.')

    def test_register_value_error(self):

        message = self.base_register(Request({'email': 'value_error'}), [])

        self.assertTrue(len(message.__dict__) == 1)
        self.assertEquals(type(message.__dict__.get('error')), ValueError)

    def test_register_attribute_error(self):

        message = self.base_register(Request({'email': 'attribute_error'}), [])

        self.assertTrue(len(message.__dict__) == 1)
        self.assertEquals(type(message.__dict__.get('error')), AttributeError)

    def test_register_validation_error(self):

        message = self.base_register(
            Request({'email': 'ok'}), ['err1', 'err2'])
        self.assertTrue(len(message.__dict__) == 0)


class Request(object):
    """ Dummy request class prividing IStatusMessage and
    behave like a dict
    """

    def __init__(self, _dict={}):
        self._dict = _dict

    def get(self, attr, default=''):
        return self._dict.get(attr, default)

    def set(self, key, value):
        self._dict[key] = value
