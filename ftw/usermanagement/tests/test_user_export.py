from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.usermanagement.tests import FunctionalTestCase
from openpyxl import load_workbook
from StringIO import StringIO
from zope.component import getMultiAdapter


class TestExportUsers(FunctionalTestCase):

    def test_decode_string_returns_unicode_string_if_utf_8(self):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')
        self.assertEqual(
            u'James B\xf6nd',
            view._decode_string('James B\xc3\xb6nd'))

    def test_decode_string_returns_unicode_string_if_unicode(self):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')
        self.assertEqual(
            u'James B\xf6nd',
            view._decode_string(u'James B\xf6nd'))

    def test_decode_string_returns_value_if_no_string(self):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')

        dummy_obj = object()

        self.assertEqual(
            dummy_obj,
            view._decode_string(dummy_obj))

    def test_attribute_names_including_additional_attributes(self):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')

        for attributename in view.additional_attribute_names:
            self.assertIn(
                attributename,
                view.attribute_names)

    def test_attribute_names_excluding_blacklist_attributes(self):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')

        for attributename in view.blacklist_attribute_names:
            self.assertNotIn(
                attributename,
                view.attribute_names)

    @browsing
    def test_validate_exported_xlsx_data(self, browser):
        self.grant('Manager')
        view = getMultiAdapter((self.portal, self.request), name='users_export')

        create(Builder('user')
               .named('Chuck', 'Norris')
               .in_groups('Administrators', 'Reviewers')
               .having(
                   home_page='http://www.test.ch',
                   location='Earth',
                   email='chuck.norris@test.ch',
                   description='Dangerous',
                   login_time=DateTime("30.12.2016 16:30")
                   ))

        wb = load_workbook(StringIO(view.export()), read_only=True)
        ws = wb.get_active_sheet()

        self.assertEqual(
            [u'description', u'home_page', u'location', u'groups', u'fullname', u'email', u'login_time'],
            [cell.value for cell in ws.rows.next()],
            "Some header rows are incorrect. Please check the output."
            )

        self.assertEqual(
            [u'Dangerous',
             u'http://www.test.ch',
             u'Earth',
             u'Administrators, Reviewers',
             u'Norris Chuck',
             u'chuck.norris@test.ch',
             datetime(2016, 12, 30, 16, 30)],
            [cell.value for cell in ws.rows.next()],
            "Some user values are incorrect. Please check the output")
