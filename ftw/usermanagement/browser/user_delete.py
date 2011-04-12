from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.usermanagement import user_management_factory as _
from Products.statusmessages.interfaces import IStatusMessage

class UserDelete(BrowserView):
    """Get a list of users from REQUEST to delete"""

    template = ViewPageTemplateFile('user_delete.pt')

    def __call__(self):
        return self.template()

    #
    # def delete(self):
    #     """delete users"""
    #
    #     userids = self.request.get('userids', [])
    #     self.delete_users(userids)
    #
    # def delete_users(self, userids):
    #
    #     if not userids:
    #         return
    #     self.mtool.deleteMembers(userids, delete_memberareas=0, delete_localroles=1, REQUEST=self.request)
    #     msg = _(u'text_user_deleted')
    #     IStatusMessage(self.request).addStatusMessage(msg, type="info")
    #     return
