from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from ftw.usermanagement import user_management_factory as _
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from itertools import chain
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

    def get_potential_groups(self, search_string):
        """Copied from plone.app.controlpanel.usergroups"""
        ignoredGroups = [x.id for x in self.get_groups() if x is not None]
        return self.membershipSearch(search_string, searchUsers=False, ignore=ignoredGroups)

    def get_display_groups(self):
        """Returns a list of dicts with name, title and is_member_of"""

        groups = []
        for g in self.membershipSearch(searchUsers=False):
            # Ignore AuthenticatedUsers group
            if g.getId() == 'AuthenticatedUsers':
                continue
            groups.append(dict(
                name=g.getId(),
                title=g.getGroupTitleOrName(),
                is_member_of = g.getId() in [g.getId() for g in self.get_groups()]))

        return groups

    def membershipSearch(self, searchString='', searchUsers=True, searchGroups=True, ignore=[]):
        """Search for users and/or groups, returning actual member and group items
           Replaces the now-deprecated prefs_user_groups_search.py script"""
        groupResults = userResults = []

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        if searchGroups:
            groupResults = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'groupid')
            groupResults = [self.gtool.getGroupById(g['id']) for g in groupResults if g['id'] not in ignore]
            groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        if searchUsers:
            userResults = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
            userResults = [self.mtool.getMemberById(u['id']) for u in userResults if u['id'] not in ignore]
            userResults.sort(key=lambda x: x is not None and x.getProperty('fullname') is not None and x.getProperty('fullname').lower() or '')

        return groupResults + userResults