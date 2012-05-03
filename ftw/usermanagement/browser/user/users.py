from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.i18n import translate
from ftw.usermanagement.browser.base_listing import BaseListing
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements
from ftw.usermanagement.interfaces import IUserManagementVocabularyFactory


class IUsersSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""


def checkbox(item, value):
    return '<input type="checkbox" name="userids" value="%s" />' % \
        item.get('userid', '')


def userpreflink(item, value):
    url = './@@user-information?userid=%s' % item.get('userid', '')
    return '<a href="%s">%s</a>' % (url, item.get('name', ''))


def link_group(item, value):

    group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                       (item.get('userid', ''), value)

    return group_link


class UserManagement(BaseListing):
    """A ftw.table based user management view
    """
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

        self.sort_order = 'ASC'
        self.batching_enabled = True
        self.lazy = False

    def __call__(self, *args, **kwargs):

        if self.table_options is None:
            self.table_options = {}

        self.update()
        return self.template()

    def get_base_query(self):
        return {}


class UsersTableSource(BaseTableSource):

    def validate_base_query(self, query):
        """Validates and fixes the base query. Returns the query object.
        """
        if not isinstance(query, dict):
            raise ValueError('Expected a dict from get_base_query() of ' + \
                                 str(self.config))

        return query

    def extend_query_with_ordering(self, query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """
        # We do not implement sorting because performance problems

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """
        query['filter_text'] = text

        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        When `lazy` is set to `True` in the configuration, this method is
        not called.
        """
        if not self.config.batching_enabled or self.config.lazy:
            query['batching'] = False
            return query

        query['pagesize'] = self.config.batching_pagesize
        query['current_page'] = self.config.batching_current_page
        query['batching'] = self.config.batching_enabled

        return query

    def search_results(self, query):
        """Executes the query and returns a tuple of `results` and `length`.
        """
        return SearchResultExecutor(self.config.context, query)()


class SearchResultExecutor(object):
    """ A fast implementation to search and display users

    This Executor just loads the data of users we see. This makes it very
    fast. If we use the filter, we need to load the data of all users,
    so it will be slower if we use him.
    """

    def __init__(self, context, query):
        self.context = context
        self.gtool = getToolByName(self.context, 'portal_groups')
        self.query = query

    def __call__(self):
        return self.get_results()

    def get_results(self):
        """ Search for users with the given paranters set in the query
        """
        mtool = getToolByName(self.context, 'portal_membership')
        users_factory = self._factory
        users_map = []

        for i, user in enumerate(users_factory):

            if not self._should_load_userdata(i):
                # If we should not load userdata, we add an empty user
                # and continue with the next item
                users_map.append(dict(
                    counter = i + 1,
                    name = '',
                    userid = user.get('id'),
                    groups = '',
                    ))
                continue

            user_info = mtool.getMemberInfo(user.get('id'))

            if not self._match_user_with_filter(user_info):
                # if the filter does not match with the userdata,
                # we continue with the next user
                continue

            users_map.append(dict(
                counter = i + 1,
                name = self._get_fullname(user_info),
                userid = user.get('id'),
                groups = self.get_group_names_of_user(user.get('id')),
                )
            )

        return users_map

    def get_group_names_of_user(self, user_id):
        """ Return all groupnames of a user as a string
        If we have no groups, we return a translated info string.
        """
        groups = []
        for group in self._get_group_objects_of_user(user_id):

            if group.getId() in ['AuthenticatedUsers']:
                continue

            groups.append(group.getGroupTitleOrName())

        groups = ', '.join(groups)

        if not groups:
            groups = translate(u'no_group',
                             domain='ftw.usermanagement',
                             context=self.context.REQUEST,
                             default=u'No Group').encode('utf-8')

        return groups

    @property
    def batch_start(self):
        """ Return the start of the batch
        """
        return self._batch_area.get('start', 0)

    @property
    def batch_end(self):
        """ Return the end of the batch
        """
        return self._batch_area.get('end', 0)

    @property
    def _batch_area(self):
        """ Return a dict with the showable area
        """
        if '_b_area' not in dir(self):
            pagesize = self.query['pagesize']
            current_page = self.query['current_page']
            self._b_area = {
                'start': pagesize * (current_page - 1),
                'end': pagesize * current_page,
                }

        return self._b_area

    @property
    def _factory(self):
        """ Return the principalsource factory
        """
        factory = getUtility(
            IUserManagementVocabularyFactory,
            name='plone.principalsource.Users')

        return factory(self.context)

    def _get_fullname(self, user_info):
        """ Get the fullname. If we have no fullname, we return the id
        """
        return user_info.get('fullname') and user_info.get('fullname') or \
            user_info.get('username')

    def _should_load_userdata(self, position):
        """ Is batching active and is the user in the area to display
        """

        # If we have nothing in the filter and the item is in the visible
        # area of the batch, then we load the userdata
        if not self.query.get('filter_text', '') and \
            (not self.query['batching'] or \
            (position >= self.batch_start and position < self.batch_end)):
            return True

        # If we have anything in the textfilter, we have to load the
        # data of all users. So we can filter
        if self.query.get('filter_text', ''):
            return True

        return False

    def _match_user_with_filter(self, user_info):
        """ Matches the filtertext with the user
        """
        text = self.query.get('filter_text', '').lower()
        if not text:
            return True

        values = ' '.join([
                user_info['username'].lower(),
                user_info['fullname'].lower(),
            ])

        return text in values

    def _cleanup_groups(self, groups):
        """ Sort and filter the given list of groups
        """
        groups.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())

        return filter(None, groups)

    def _get_group_objects_of_user(self, user_id):
        """ Return all groupobjects of a given user
        """
        groups = self.gtool.getGroupsByUserId(user_id)

        groups = self._cleanup_groups(groups)

        return groups