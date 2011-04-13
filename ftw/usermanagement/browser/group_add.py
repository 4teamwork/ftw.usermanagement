from ftw.usermanagement import user_management_factory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class GroupAdd(BrowserView):

    def __init__(self, context, request):
        super(GroupAdd, self).__init__(context, request)

        self.gtool = getToolByName(self, 'portal_groups')

    def __call__(self):
        self.create_group();


    def create_group(self):
        """Validates input and creates a new group"""

        # XXX: Validate input
        group_id = self.request.get('group_id', '')
        group_title = self.request.get('group_title', group_id)

        if not group_title:
            group_title = group_id

        if group_id:
            data = dict(title=group_title)
            success = self.gtool.addGroup(group_id, **data)
            if not success:
                # reset group_id
                group_id = ''

        if group_id:
            # Successfully created group
            msg = _(u'text_group_created')
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type="info")
        else:
            msg = _(u'text_enter_valid_group_id')
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type="error")
        return True
