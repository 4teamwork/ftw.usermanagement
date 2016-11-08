from DateTime import DateTime
from datetime import datetime
from ftw.usermanagement.browser.user.users import UsersSearchResultExecutor
from plone import api
from StringIO import StringIO
from xlsxwriter.workbook import Workbook


class UserExport(object):

    filename = 'member_export.xlsx'
    contenttype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    blacklist_attribute_names = [
        'visible_ids',
        'wysiwyg_editor',
        'error_log_update',
        'listed',
        'language',
        'portal_skin',
        'ext_editor',
        'last_login_time',
    ]

    additional_attribute_names = [
        'groups'
    ]

    def __call__(self):
        self.request.response.setHeader("Content-type", self.contenttype)
        self.request.response.setHeader(
            "Content-Disposition", 'inline; filename="%s"' % self.filename)
        return self.export()

    def export(self):
        output = StringIO()

        workbook = Workbook(output)
        default_format = workbook.add_format()
        datetime_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})

        worksheet = workbook.add_worksheet('User export')
        worksheet.write_row(0, 0, self.attribute_names)

        users = api.user.get_users()
        for row, user in enumerate(users):
            for column, prop in enumerate(self.attribute_names):
                value = user.getProperty(prop, '')
                cell_format = default_format

                if isinstance(value, DateTime):
                    value = value.asdatetime()

                if isinstance(value, datetime):
                    value = value.replace(tzinfo=None)
                    cell_format = datetime_format

                if prop == 'groups':
                    value = self._get_groups_of_user(user)

                worksheet.write(
                    row+1, column, self._decode_string(value), cell_format)

        if users:
            worksheet.autofilter(0, 0, len(users)+1, len(self.attribute_names))

        workbook.close()

        output.seek(0)
        return output.read()

    @property
    def attribute_names(self):
        """Returns the attribute names which should be exported.
        """
        if not hasattr(self, '_attribute_names'):
            attribute_names = self._get_member_data_propertie_names()
            attribute_names.extend(self.additional_attribute_names)
            attribute_names = list(set(attribute_names) - set(self.blacklist_attribute_names))
            setattr(self, '_attribute_names', attribute_names)

        return getattr(self, '_attribute_names')

    def _decode_string(self, value):
        if isinstance(value, str):
            return value.decode('utf-8')
        return value

    def _get_user_search_result_executor(self):
        if not hasattr(self, '_user_search_result_executor'):
            setattr(self, '_user_search_result_executor',
                    UsersSearchResultExecutor(
                        self.context, query=None, is_email_login=None)
                    )
        return getattr(self, '_user_search_result_executor')

    def _get_groups_of_user(self, user):
        """ Return all groupnames of a user as a string
        If we have no groups, we return a translated info string.
        """
        return self._get_user_search_result_executor().get_group_names_of_user(
            user.getId())

    def _get_member_data_propertie_names(self):
        memberdata = api.portal.get_tool('portal_memberdata')
        return memberdata.propdict().keys()
