from Products.CMFCore.utils import getToolByName
from ftw.usermanagement import user_management_factory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.usergroups import UsersGroupsControlPanelView


class UserMembership(UsersGroupsControlPanelView):
    """Provides another way to assign groups to a member"""

    template = ViewPageTemplateFile('user_membership.pt')

    def __call__(self):
        """ Check the given request parameters and call the
        correct functions
        """
        form = self.request.form
        user_id = self.request.get('userid', None)
        groups = form.get('new_groups', [])

        if not user_id:
            return 'No user selected'

        if not form.get('form.submitted', False):
            return self.render(user_id)

        return self.replace_groups(user_id, groups)

    def render(self, user_id):
        """ Renders the popup to assign new groups
        """
        users = self.get_display_groups(user_id)
        return self.template(users=users)

    def replace_groups(self, user_id, groups):
        """ Replace the assigned group in the groups-attr
        """
        gtool = getToolByName(self.context, 'portal_groups')
        current_groups = self.get_groups(user_id)

        # Remove unselected groups
        for group in current_groups:
            if group == 'AuthenticatedUsers':
                continue
            if group not in groups:
                gtool.removePrincipalFromGroup(user_id, group, self.request)

        # Add member to groups
        for group in groups:
            if group not in current_groups:
                gtool.addPrincipalToGroup(user_id, group, self.request)

        IStatusMessage(self.request).addStatusMessage(
            _(u'Changes made.'), type="info")

        return True

    def get_groups(self, user_id):
        """Return a sorted list of group ids the user is member of
        """
        gtool = getToolByName(self.context, 'portal_groups')
        mtool = getToolByName(self.context, 'portal_membership')

        member = mtool.getMemberById(user_id)
        groups = gtool.getGroupsForPrincipal(member)

        group_results = [gtool.getGroupById(m) for m in groups]

        group_results.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        group_results = filter(None, group_results)
        group_ids = [group.getId() for group in group_results]
        return group_ids

    def get_display_groups(self, user_id):
        """Returns a list of dicts with name, title and is_member_of"""

        groups = []
        current_groups = self.get_groups(user_id)

        for g in self.membershipSearch(searchUsers=False):
            # Ignore AuthenticatedUsers group
            if g.getId() == 'AuthenticatedUsers':
                continue
            groups.append(dict(
                name=g.getId(),
                title=g.getGroupTitleOrName(),
                is_member_of=g.getId() in current_groups))

        return groups
