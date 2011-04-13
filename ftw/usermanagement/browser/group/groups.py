from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryMultiAdapter
from ftw.usermanagement.browser.base_listing import BaseListing
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements
from ftw.table.basesource import BaseTableSource

class IGroupsSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""



def checkbox(item, value):
     return '<input type="checkbox" name="groupids" value="%s" />' % \
        item['group_id']

class GroupManagement(BaseListing):
    """
    A ftw.table based user management view
    """
    implements(IGroupsSourceConfig)

    columns = (
        {'column': 'counter',
         'column_title': _(u'label_nr', default='Nr.'),
         },
        {'transform': checkbox},
        {'column': 'group_title',
         'column_title': _(u'label_group_title', default='Title'), },
        {'column': 'group_id',
         'column_title': _(u'label_group_id', default='Id'), },
        # {'column': 'group_members',
        #  'column_title': _(u'label_group_members', default='Members'), }
        )


    template = ViewPageTemplateFile('groups.pt')


    def __call__(self):

        if self.table_options is None:
            self.table_options = {}

        self.update()
        return self.template()

    def __init__(self, context, request):
        super(GroupManagement, self).__init__(context, request)

        self.context = context
        self.request = request
        self.sort_on = 'group_title'

        self.gtool = getToolByName(self, 'portal_groups')

        self.groupprefs = queryMultiAdapter((context, request),
                                         name=u'usergroup-groupprefs')

    def groups(self):
        groups = self.groupprefs.doSearch(searchString='')
        results = []
        for g in groups:
            if 'AuthenticatedUsers' != g['groupid']:
                results.append(dict(
                    group_id=g['groupid'],
                    group_title=g['title'],
                    group_members=''))
        return results

    def create_group(self):
        """Validates input and creates a new group"""

        # XXX: Validate input
        group_id = self.request.get('group_id', '')
        group_title = self.request.get('group_title', group_id)

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
        return self.template()


    def get_base_query(self):
        query = self.groups()
        return query


class GroupsTableSource(BaseTableSource):

    def validate_base_query(self, query):
        return query

    def search_results(self, results):

        search = self.config.filter_text.lower()

        if search:

            def filter_(item):
                searchable = ' '.join((item['group_title'], item['group_id'])).lower()
                return search in searchable
            return filter(filter_, results)
        return results