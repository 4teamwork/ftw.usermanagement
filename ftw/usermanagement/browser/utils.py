from zope.component import getMultiAdapter
from Acquisition import aq_inner
from itertools import chain
from Products.CMFCore.utils import getToolByName

def membership_search(context, searchString='', searchUsers=True, searchGroups=True, ignore=[]):
    """Search for users and/or groups, returning actual member and group items
       Replaces the now-deprecated prefs_user_groups_search.py script"""
    groupResults = userResults = []
    request = context.REQUEST
    gtool = getToolByName(context, 'portal_groups')
    mtool = getToolByName(context, 'portal_membership')

    searchView = getMultiAdapter((aq_inner(context), request), name='pas_search')

    if searchGroups:
        groupResults = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'groupid')
        groupResults = [gtool.getGroupById(g['id']) for g in groupResults if g['id'] not in ignore]
        groupResults.sort(key=lambda x: x is not None and x.getGroupTitleOrName().lower())

    if searchUsers:
        userResults = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
        userResults = [mtool.getMemberById(u['id']) for u in userResults if u['id'] not in ignore]
        userResults.sort(key=lambda x: x is not None and x.getProperty('fullname') is not None and x.getProperty('fullname').lower() or '')

    return groupResults + userResults
