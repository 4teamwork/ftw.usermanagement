from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from ftw.usermanagement.browser.base_listing import BaseListing
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements


class IUsersSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""


def checkbox(item, value):
    return '<input type="checkbox" name="userids" value="%s" />' % \
        item['userid']


def userpreflink(item, value):
    url = './@@user-information?userid=%s' % item['userid']
    return '<a href="%s">%s</a>' % (url, item['name'])

def link_group(item, value):

    group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                       (item['userid'], value)

    return group_link

class UserManagement(BaseListing):
    """A ftw.table based user management view"""
    implements(IUsersSourceConfig)

    show_menu = False
    show_selects = True

    columns = (
        {'column': 'counter',
         'column_title': _(u'label_nr', default='Nr.'),
         },
        {'transform': checkbox},
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'),
         'transform': userpreflink},
        {'column': 'userid',
         'column_title': _(u'label_userid', default='Userid'), },
        {'column': 'groups',
         'column_title': _(u'label_groups', default='Groups'),
         'transform': link_group })


    template = ViewPageTemplateFile('users.pt')

    def __init__(self, context, request):
        super(UserManagement, self).__init__(context, request)
        self.context = context
        self.request = request

        self.acl_users = getToolByName(context, 'acl_users')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')
        self.pagenumber = 1
        self.sort_order = 'ASC'
        self.contents = self.users()
        self.sort_on = 'name'

    def __call__(self, *args, **kwargs):

        if self.table_options is None:
            self.table_options = {}

        self.update()

        return self.template()

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
                          default=u'No Group')
                    # / -- i18ndude hint --
                    # do not use translation messages - translate directly
                    user_groups = translate(u'no_group',
                                     domain='ftw.usermanagement',
                                     context=self.request,
                                     default=u'No Group').encode('utf-8')
                #
                # group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                #                    (t.value, user_groups)
                userinfo = dict(
                    counter = index + 1,
                    name = t.title,
                    userid = t.token,
                    groups = user_groups)
                users.append(userinfo)

        return users

    def groups_by_member(self, userid):
        groupResults = [self.gtool.getGroupById(m) \
            for m in self.gtool.getGroupsForPrincipal(userid)]
        groupResults.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groupResults)

    def get_base_query(self):
        query = self.contents
        return query


class UsersTableSource(BaseTableSource):

    def validate_base_query(self, query):
        return query

    def search_results(self, results):

        search = self.config.filter_text.lower()

        if search:
            def filter_(item):
                searchable = ' '.join((item['name'], item['userid'], item['groups'])).lower()
                return search in searchable
            return filter(filter_, results)
        return results
