from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class GroupAdd(BrowserView):

    def __call__(self):

        group_id = self.request.get('group_id', '')
        group_title = self.request.get('group_title', group_id)

        self.create_group(group_id, group_title)

    def create_group(self, group_id, group_title):
        """Creates a new group
        """
        gtool = getToolByName(self.context, 'portal_groups')

        if not self.validate_group(group_id):
            return False

        data = dict(title=group_title or group_id)
        gtool.addGroup(group_id, **data)

        self._add_statusmessage(_(u'text_group_created'), "info")

        return True

    def validate_group(self, group_id):
        """ Validates the input
        """
        registration = getToolByName(self.context, 'portal_registration')
        no_errors = True

        # check if group_id is allowed
        if not registration.isMemberIdAllowed(group_id):
            msg = _(u"The group id you selected is already"
                "in use or is not valid. Please choose another.")
            self._add_statusmessage(msg, "error")
            no_errors = False

        return no_errors

    def _add_statusmessage(self, msg, mtype):
        """ Add a statusmessage
        """
        IStatusMessage(self.request).addStatusMessage(msg, type=mtype)
