from AccessControl import getSecurityManager
from ftw.usermanagement import user_management_factory as _
from plone.app.controlpanel.usergroups import UsersGroupsControlPanelView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zExceptions import Unauthorized


class GroupMembership(UsersGroupsControlPanelView):
    """Provides another way to assign users to a group
    """

    template = ViewPageTemplateFile('group_membership.pt')
    roles_required_template = ViewPageTemplateFile('error_roles_required.pt')
    admin_roles = set(('Site Administrator', 'Manager'))

    def __call__(self):
        """ Check the given request parameters and call the
        correct functions
        """
        form = self.request.form
        group_id = self.request.get('group_id', None)
        users = form.get('new_users', [])

        if not group_id:
            raise BadRequest('Missing parameter group_id.')

        required_roles = self.missing_roles_for_management(group_id)

        if form.get('form.submitted'):
            if required_roles:
                raise Unauthorized()
            else:
                return self.replace_group_members(group_id, users)

        if required_roles:
            return self.roles_required_template(required_roles=required_roles)
        else:
            return self.render(group_id)

    def missing_roles_for_management(self, group_id):
        """Returns a list of roles which the user requires for
        changing the membership of this group.
        When the returned list is empty, the user is allowed to edit.
        """
        gtool = getToolByName(self.context, 'portal_groups')
        group_roles = set(gtool.getGroupById(group_id).getRoles())
        current_user_roles = set(getSecurityManager().getUser().getRoles())

        required_roles = group_roles & self.admin_roles
        missing_roles = required_roles - current_user_roles
        return tuple(missing_roles)

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
        clean_members = []
        for member in group_members:
            user_info = mtool.getMemberInfo(member)
            if not user_info:
                continue
            clean_members.append(member)
        clean_members.sort(key=sort_users)

        return filter(None, group_members)

    def get_display_users(self, group_id):
        """ Returns a list of dicts with name, title and is_member_of
        """
        users = []
        current_users = self.get_users(group_id)

        for m in self.membershipSearch(searchGroups=False):
            if m is not None:
                fullname = m.getProperty('fullname', m.getUserId())
                users.append(dict(
                    userid=m.getUserId(),
                    name=fullname and fullname or m.getUserId(),
                    is_member_of=m.getUserId() in current_users))

        return users
