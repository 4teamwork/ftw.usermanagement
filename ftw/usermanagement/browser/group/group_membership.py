from Products.CMFCore.utils import getToolByName
from ftw.usermanagement import user_management_factory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.usergroups import UsersGroupsControlPanelView


class GroupMembership(UsersGroupsControlPanelView):
    """Provides another way to assign users to a group
    """

    template = ViewPageTemplateFile('group_membership.pt')

    def __call__(self):
        """ Check the given request parameters and call the
        correct functions
        """
        form = self.request.form
        group_id = self.request.get('group_id', None)
        users = form.get('new_users', [])

        if not group_id:
            # Fallback
            return 'No group selected'

        if not form.get('form.submitted', False):
            return self.render(group_id)

        return self.replace_group_members(group_id, users)

    def render(self, group_id):
        """ Renders the popup to assign new users
        """
        users = self.get_display_users(group_id)
        return self.template(users=users)

    def replace_group_members(self, group_id, users):
        """ Replace the assigned users in the users-attr
        """
        current_users = self.get_users(group_id)
        gtool = getToolByName(self.context, 'portal_groups')

        # Remove unselected users
        for user in current_users:
            if user in users:
                continue
            gtool.removePrincipalFromGroup(user, group_id, self.request)

        # Add users to groups
        for user in users:
            if user in current_users:
                continue
            gtool.addPrincipalToGroup(user, group_id, self.request)

        IStatusMessage(self.request).addStatusMessage(
            _(u'Changes made.'), type="info")

        return True

    def get_users(self, group_id):
        """ Return a sorted list of users assigned to a group
        """
        gtool = getToolByName(self.context, 'portal_groups')
        mtool = getToolByName(self.context, 'portal_membership')

        def sort_users(user):
            member = mtool.getMemberById(user)
            if not member:
                return user
            fullname = member.getProperty('fullname', '')
            if not fullname:
                return user
            return fullname

        group_members = gtool.getGroupMembers(group_id)
        group_members.sort(key=sort_users)

        return filter(None, group_members)

    def get_display_users(self, group_id):
        """ Returns a list of dicts with name, title and is_member_of
        """
        users = []
        current_users = self.get_users(group_id)

        for m in self.membershipSearch(searchGroups=False):
            fullname = m.getProperty('fullname', m.getUserId())
            users.append(dict(
                userid=m.getUserId(),
                name=fullname and fullname or m.getUserId(),
                is_member_of=m.getUserId() in current_users))

        return users
