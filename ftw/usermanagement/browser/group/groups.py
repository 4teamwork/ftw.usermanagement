from ftw.usermanagement import user_management_factory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from ftw.usermanagement.browser.base_listing import \
    BaseListing, BaseManagementTableSource, BaseSearchResultExecutor
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements
import urllib


class IGroupsSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""


def checkbox(item, value):
    return '<input type="checkbox" name="groupids" value="%s" />' % \
        item['group_id']


def link_group(item, value):

    group_link = '<a href="./group_membership?group_id=%s">%s</a>' % \
                       (urllib.quote(item['group_id']), value)

    return group_link


class GroupManagement(BaseListing):
    """A ftw.table based user management view"""

    implements(IGroupsSourceConfig)

    show_menu = False

    columns = (
        {'column': 'counter',
         'column_title': _(u'label_nr', default='Nr.'),
         },
        {'transform': checkbox},
        {'column': 'group_title',
         'column_title': _(u'label_group_title', default='Title'),
         'transform': link_group},
        {'column': 'group_id',
         'column_title': _(u'label_group_id', default='Id'), },
        )

    template = ViewPageTemplateFile('groups.pt')


class GroupsTableSource(BaseManagementTableSource):

    def search_results(self, query):
        """Executes the query and returns a tuple of `results` and `length`.
        """
        return GroupsSearchResultExecutor(self.config.context, query)()


class GroupsSearchResultExecutor(BaseSearchResultExecutor):
    """ Search and display groups
    """

    def get_results(self):
        """ Get title and id of all groups
        """
        groupprefs = queryMultiAdapter((self.context, self.context.REQUEST),
                                         name=u'usergroup-groupprefs')
        groups = groupprefs.doSearch(searchString='')
        results = []

        for group in groups:
            if group['groupid'] in ['AuthenticatedUsers']:
                continue

            if not self._match_obj_with_filter(
                group, ['groupid', 'title']):
                continue

            results.append(dict(
                group_id=group['groupid'],
                group_title=group['title'], ),
            )

        results = self._sort_groups(results)

        return results

    def _sort_groups(self, group):
        """ Sort the group by title
        """
        group.sort(key=lambda x: x.get('group_title'))

        return group
