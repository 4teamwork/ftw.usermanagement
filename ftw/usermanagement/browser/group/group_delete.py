from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage


class GroupDelete(BrowserView):
    """Get a list of groups from REQUEST to delete"""

    template = ViewPageTemplateFile('group_delete.pt')

    def __call__(self):
        return self.template()

    def delete(self):
        """Delete groups"""

        groupids = self.request.get('groupids', [])
        groupids = isinstance(groupids, list) and groupids or [groupids]

        try:
            getToolByName(self, 'portal_groups').removeGroups(groupids)
        except KeyError:
            IStatusMessage(self.request).addStatusMessage(
                _(u'There was an error while deleting a group.'), type="error")
            return

        IStatusMessage(self.request).addStatusMessage(
            _(u'Group(s) deleted.'), type="info")
