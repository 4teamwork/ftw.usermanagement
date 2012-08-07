from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.usermanagement import user_management_factory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName


class UserDelete(BrowserView):
    """Get a list of users from REQUEST to delete"""

    template = ViewPageTemplateFile('user_delete.pt')

    def __call__(self):
        return self.template()

    def delete(self):
        """delete users"""
        userids = self.request.get('userids', [])
        mtool = getToolByName(self, 'portal_membership')
        mtool.deleteMembers(
            userids,
            delete_memberareas=1,
            delete_localroles=0,
            REQUEST=self.request,
            )

        IStatusMessage(self.request).addStatusMessage(
            _(u'text_user_deleted'), type="info")
