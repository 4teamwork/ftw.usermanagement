from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class GroupAdd(BrowserView):

    def __init__(self, context, request):
        super(GroupAdd, self).__init__(context, request)

        self.gtool = getToolByName(self, 'portal_groups')
        self.registration = getToolByName(self.context, 'portal_registration')

    def __call__(self):
        self.validate_group()

    def validate_group(self):

        errors = {}
        group_id = self.request.get('group_id', '')

        # check if group_id is allowed
        if not 'group_id' in errors:
            if not self.registration.isMemberIdAllowed(group_id):
                errors['group_id'] = _(u"The group id you selected is already"
                    "in use or is not valid. Please choose another.")


        if errors:
            self.request.set('errors', errors)
            for field, msg in errors.items():
                IStatusMessage(self.request).addStatusMessage(
                    msg,
                    type="error")
            return False
        else:
            self.create_group()


    def create_group(self):
        """Validates input and creates a new group"""

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
