from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from ftw.usermanagement import user_management_factory as _
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from itertools import chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GroupMembership(BrowserView):
    """Provides another way to assign users to a group"""

    template = ViewPageTemplateFile('group_membership.pt')

    def __call__(self):

        self.gtool = getToolByName(self.context, 'portal_groups')
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.group_id = self.request.get('group_id', None)
        if self.group_id is None:
            return 'No group selected'
        #self.member = self.mtool.getGroupById(self.group_id)
        self.search_string = ''

        form = self.request.form
        self.current_users = self.get_users()

        if form.get('form.submitted', False):
            new_users = form.get('new_users', [])
            # Remove unselected users
            for m in self.current_users:
                if m not in new_users:
                    self.gtool.removePrincipalFromGroup(
                        m,
                        self.group_id,
                        self.request,
                        )

            # Redefine current_groups
            # XXX Do not call self.get_users twice
            self.current_users = self.get_users()
            # Add member to groups
            for m in new_users:
                if m not in self.current_users:
                    self.gtool.addPrincipalToGroup(
                        m,
                        self.group_id,
                        self.request,
                        )

            self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            # XXX Do not call self.get_users three times
            self.current_users = self.get_users()

        return self.template()

    def get_users(self):
        """Copied from plone.app.controlpanel.usergroups"""
        def sort_users(user):
            member = self.mtool.getMemberById(user)
            if not member:
                return user
            fullname = self.mtool.getMemberById(user).getProperty('fullname', '')
            if  not fullname:
                return user
            return fullname

        group_members = self.gtool.getGroupMembers(self.group_id)
        group_members.sort(key=sort_users)
        return filter(None, group_members)

    def get_display_users(self):
        """Returns a list of dicts with name, title and is_member_of"""
        users = []
        for m in self.membershipSearch(searchGroups=False):
            fullname = m.getProperty('fullname', m.getUserId())
            users.append(dict(
                userid=m.getUserId(),
                name=fullname and fullname or m.getUserId(),
                is_member_of = m.getUserId() in self.get_users()))

        return users

    #XXX - rRefactor same method is defined in user_membership.py
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
