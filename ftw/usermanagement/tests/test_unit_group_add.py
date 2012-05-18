# coding=UTF-8
from ftw.testing import MockTestCase
from mocker import ANY, KWARGS
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.group.group_add import GroupAdd
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class ValidateGroupTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(ValidateGroupTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.rtool = self.mocker.mock(count=False)
        self.mock_tool(self.rtool, 'portal_registration')
        self.expect(self.rtool.isMemberIdAllowed('invalid')).result(False)
        self.expect(self.rtool.isMemberIdAllowed('valid')).result(True)

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_invalid_id(self):

        self.replay()

        result = GroupAdd(self.context, self.request).validate_group('invalid')

        self.assertEqual(result, False)
        self.assertEqual(
            self.message_cache.error,
            u"The group id you selected is already"
            "in use or is not valid. Please choose another.")

    def test_valid_id(self):

        self.replay()

        result = GroupAdd(self.context, self.request).validate_group('valid')

        self.assertEqual(result, True)


class AddGroupTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(AddGroupTests, self).setUp()

        self.request = {}
        self.context = self.stub()

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')
        self.group_pool = {}
        self.expect(self.gtool.addGroup(ANY, KWARGS)).call(
            lambda x, title: self.group_pool.update({x: title}))

        self.statusmsg = self.mocker.mock(count=False)
        self.message_cache = self.create_dummy()
        self.expect(self.statusmsg(ANY).addStatusMessage(ANY, type=ANY)).call(
            lambda msg, type: setattr(self.message_cache, type, msg))
        self.mock_adapter(self.statusmsg, IStatusMessage, (Interface, ))

    def test_create_group_invalid_id(self):

        group_add = self.mocker.patch(GroupAdd(self.context, self.request))
        self.expect(group_add.validate_group(ANY)).result(False)

        self.replay()

        result = group_add.create_group('invalid_id', 'title')

        self.assertEqual(result, False)
        self.assertEqual(self.group_pool, {})

    def test_create_group_no_title(self):

        group_add = self.mocker.patch(GroupAdd(self.context, self.request))
        self.expect(group_add.validate_group(ANY)).result(True)

        self.replay()

        result = group_add.create_group('group_id', '')

        self.assertTrue

        self.assertEqual(result, True)
        self.assertEqual(self.message_cache.info, u'text_group_created')
        self.assertEqual(self.group_pool, {'group_id': 'group_id'})

    def test_create_group(self):

        group_add = self.mocker.patch(GroupAdd(self.context, self.request))
        self.expect(group_add.validate_group(ANY)).result(True)

        self.replay()

        result = group_add.create_group('group_id', 'Ädmin')

        self.assertTrue

        self.assertEqual(result, True)
        self.assertEqual(self.message_cache.info, u'text_group_created')
        self.assertEqual(self.group_pool, {'group_id': 'Ädmin'})
