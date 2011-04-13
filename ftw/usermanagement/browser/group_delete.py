from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.usermanagement import user_management_factory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName


class GroupDelete(BrowserView):
    """Get a list of groups from REQUEST to delete"""

    template = ViewPageTemplateFile('group_delete.pt')

    def __init__(self, context, request):
        super(GroupDelete, self).__init__(context, request)

        self.mtool = getToolByName(self, 'portal_membership')
        self.gtool = getToolByName(self, 'portal_groups')

    def __call__(self):
        return self.template()

    def delete(self):
        """delete groups"""

        groupids = self.request.get('groupids', [])

        if type(groupids) != list:
            groupids = [groupids]

        self.delete_groups(groupids)

    def delete_groups(self, groupids):
        if groupids:

            self.gtool.removeGroups(groupids)
            msg = _(u'Group(s) deleted.')

            IStatusMessage(self.request).addStatusMessage(
                msg,
                type="info")
        return
