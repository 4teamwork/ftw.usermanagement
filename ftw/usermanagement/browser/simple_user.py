from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility, getUtility
from zope.i18n import translate
from ftw.tabbedview.browser.listing import ListingView
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from ftw.table.basesource import BaseTableSource
from zope.interface import implements
from operator import itemgetter

def checkbox(item, value):
     return '<input type="checkbox" name="userids:list" value="%s" />' % \
        item['email']

def userpreflink(item, value):
    url = './@@user-information?userid=%s' % item['email']
    return '<a href="%s">%s</a>' % (url, item['name'])


class ISimpleSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""

class UserManagement(ListingView):
    """
    A ftw.table based user management view
    """
    implements(ISimpleSourceConfig)

    columns = (
        {'column': 'counter',
         'column_title': _(u'label_nr', default='Nr.'),
         },
        {'transform': checkbox},
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'),
         'transform': userpreflink},
        {'column': 'email',
         'column_title': _(u'label_email', default='Email'), },
        {'column': 'groups',
         'column_title': _(u'label_groups', default='Groups'), })


    template = ViewPageTemplateFile('simple_user.pt')

    def __init__(self, context, request):
        super(UserManagement, self).__init__(context, request)
        self.context = context
        self.request = request

        self.acl_users = getToolByName(context, 'acl_users')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')
        self.pagenumber = 1
        self.pagesize = 5
        self.sort_order = 'ASC'
        self.contents = self.users()
        self.sortable = True
        self.sort_on = 'name'

    def users(self):
        context = self.context
        users = []
        factory = getUtility(
            schema.interfaces.IVocabularyFactory,
            name='plone.principalsource.Users',
            context=context)

        if factory:
            users_terms = factory(context)

            # convert to a dict for now, because ftw.table cannot hanndle
            # SimpleTerms
            for index, t in enumerate(users_terms):
                member = self.mtool.getMemberById(t.token)
                user_groups = []
                for g in self.groups_by_member(member):
                    groupname = g.getId()
                    if 'AuthenticatedUsers' != groupname:
                        user_groups.append(g.getGroupTitleOrName())

                if user_groups:
                    user_groups = ', '.join(user_groups)
                else:
                    if 0:
                    # -- i18ndude hint --
                        _(u'no_group',
                          default=u'No Group',)
                    # / -- i18ndude hint --
                    # do not use translation messages - translate directly
                    user_groups = translate(u'no_group',
                                     domain='ftw.usermanagement',
                                     context=self.request,
                                     default=u'No Group')

                group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                    (t.value, user_groups)

                userinfo = dict(
                    counter = index + 1,
                    name = t.title,
                    email = t.value,
                    groups = group_link)
                users.append(userinfo)

        return users

    def groups_by_member(self, userid):
        groupResults = [self.gtool.getGroupById(m) \
            for m in self.gtool.getGroupsForPrincipal(userid)]
        groupResults.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groupResults)

    def search(self, kwargs):
        search = kwargs.get('SearchableText', None)
        if search:
            search = search.lower()

        self.contents = self.users()

        if search:

            def filter_(item):
                searchable = ' '.join((item['name'], item['mail'])).lower()
                return search in searchable

            self.contents = filter(filter_, self.contents)
        self.len_results = len(self.contents)

    def get_base_query(self):
        query = self.users()
        return query

    def batch_template(self):

        return self.batching()

    def _custom_sort_method(self, results, sort_on, sort_reverse):

        results.sort(key=itemgetter(sort_on))

        if sort_reverse:
            results.reverse()

        return results

class SimpleTableSource(BaseTableSource):


    def validate_base_query(self, query):
        return query

    def search_results(self, results):
        return results