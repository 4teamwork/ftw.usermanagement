from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from ftw.usermanagement import user_management_factory as _
from ftw.usermanagement.browser.utils import membership_search
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class UserMembership(BrowserView):
    """Provides another way to assign groups to a member"""

    template = ViewPageTemplateFile('user_membership.pt')

    def __call__(self):

        self.gtool = getToolByName(self.context, 'portal_groups')
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.userid = self.request.get('userid', None)
        if self.userid is None:
            return 'No user selected'
        self.member = self.mtool.getMemberById(self.userid)
        self.search_string = ''

        form = self.request.form
        self.current_groups = [g.getId() for g in self.get_groups()]


        if form.get('form.submitted', False):
            new_groups = form.get('new_groups', [])

            # Remove unselected groups
            for g in self.current_groups:
                if g == 'AuthenticatedUsers':
                    continue
                if g not in new_groups:
                    self.gtool.removePrincipalFromGroup(
                        self.userid,
                        g,
                        self.request,
                        )


            # XXX: If we call self.get_groups after removing an item,
            # it will be still there?

            # Redefine current_groups
            self.current_groups = [g.getId() for g in self.get_groups()]
            # Add member to groups
            for g in new_groups:
                if g not in self.current_groups:
                    self.gtool.addPrincipalToGroup(
                        self.userid,
                        g,
                        self.request,
                        )

            self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            self.current_groups = [g.getId() for g in self.get_groups()]

        return self.template()

    def get_groups(self):
        """Copied from plone.app.controlpanel.usergroups"""
        groupResults = [self.gtool.getGroupById(m) for m in self.gtool.getGroupsForPrincipal(self.member)]
        groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groupResults)

    def get_display_groups(self):
        """Returns a list of dicts with name, title and is_member_of"""

        groups = []
        for g in membership_search(self.context, searchUsers=False):
            # Ignore AuthenticatedUsers group
            if g.getId() == 'AuthenticatedUsers':
                continue
            groups.append(dict(
                name=g.getId(),
                title=g.getGroupTitleOrName(),
                is_member_of = g.getId() in [g.getId() for g in self.get_groups()]))

        return groups
