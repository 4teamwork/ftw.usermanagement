from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.i18n import translate
from ftw.usermanagement.browser.base_listing import \
    BaseListing, BaseManagementTableSource, BaseSearchResultExecutor
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

    template = ViewPageTemplateFile('users.pt')

    def __init__(self, context, request):
        super(UserManagement, self).__init__(context, request)

        self.sort_order = 'ASC'
        self.batching_enabled = True
        self.lazy = False

    @property
    def columns(self):
        base_columns = (
            {'column': 'counter',
             'column_title': _(u'label_nr', default='Nr.'),
             },
            {'transform': checkbox},
            {'column': 'name',
             'column_title': _(u'label_name', default='Name'),
             'transform': userpreflink},
            {'column': 'login',
             'column_title': _(u'label_login', default='login'), },
            {'column': 'groups',
             'column_title': _(u'label_groups', default='Groups'),
             'transform': link_group})

        if not self.is_email_login():
            base_list = list(base_columns)
            base_list.insert(4, {'column': 'email',
             'column_title': _(u'label_email', default='E-Mail')},
            )
            base_columns = tuple(base_list)

        return tuple(base_columns)

    def is_email_login(self):
        prop_tool = getToolByName(self.context, 'portal_properties')
        return prop_tool.site_properties.getProperty('use_email_as_login')


class UsersTableSource(BaseManagementTableSource):

    def search_results(self, query):
        """Executes the query and returns a tuple of `results` and `length`.
        """
        return UsersSearchResultExecutor(self.config.context, query,
                                         self.config.is_email_login())()


class UsersSearchResultExecutor(BaseSearchResultExecutor):
    """ A fast implementation to search and display users

    This Executor just loads the data of users we see. This makes it very
    fast. If we use the filter, we need to load the data of all users,
    so it will be slower if we use him.
    """

    def __init__(self, context, query, is_email_login):
        super(UsersSearchResultExecutor, self).__init__(context, query)

        self.gtool = getToolByName(self.context, 'portal_groups')
        self._b_area = None
        self.is_email_login = is_email_login

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
                    counter=i + 1,
                    name='',
                    userid=user.get('id'),
                    groups='',
                    ))
                continue

            # This is very expensive. We need the memberinfo because we
            # need the fullname. Thats not stored in acl_users.
            user_info = mtool.getMemberInfo(user.get('id'))
            if not user_info:
                continue

            if not self._match_obj_with_filter(
                user_info, ['username', 'fullname']):
                # if the filter does not match with the userdata,
                # we continue with the next user
                continue

            # We need to use the login name to get the group because a plone
            # function is decleared wrong
            if self.is_email_login:
                users_map.append(dict(
                    counter=i + 1,
                    name=self._get_fullname(user_info),
                    login=user.get('login'),
                    userid=user.get('id'),
                    groups=self.get_group_names_of_user(user.get('login')),
                    )
                )
            else:
                member = mtool.getMemberById(user.get('id'))
                email = member.getProperty('email')
                users_map.append(dict(
                    counter=i + 1,
                    name=self._get_fullname(user_info),
                    login=user.get('login'),
                    userid=user.get('id'),
                    email=email,
                    groups=self.get_group_names_of_user(user.get('login')),
                    )
                )

        return users_map

    def get_group_names_of_user(self, loginname):
        """ Return all groupnames of a user as a string
        If we have no groups, we return a translated info string.
        """
        groups = []
        for group in self._get_group_objects_of_user(loginname):

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
        if not self._b_area:
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
           (not self.query['batching'] or (
               position >= self.batch_start and position < self.batch_end)):
            return True

        # If we have anything in the textfilter, we have to load the
        # data of all users. So we can filter
        if self.query.get('filter_text', ''):
            return True

        return False

    def _cleanup_groups(self, groups):
        """ Sort and filter the given list of groups
        """
        groups.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groups)

    def _get_group_objects_of_user(self, loginname):
        """ Return all groupobjects of a given user
        """

        # This Function requires the login name and not the userid
        groups = self.gtool.getGroupsByUserId(loginname)

        groups = self._cleanup_groups(groups)

        return groups
