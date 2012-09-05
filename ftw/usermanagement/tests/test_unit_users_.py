from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.users import UsersSearchResultExecutor
from ftw.usermanagement.interfaces import IUserManagementVocabularyFactory


class GroupNamesOfUserTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(GroupNamesOfUserTests, self).setUp()

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.context)

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

    def test_no_groups(self):

        self.expect(self.gtool.getGroupsByUserId(ANY)).result([])

        self.replay()

        executor = UsersSearchResultExecutor(self.context, '', True)
        result = executor.get_group_names_of_user('user')

        self.assertEquals(result, 'No Group')

    def test_unsorted_groups(self):

        groups = [Group('group%s' % i) for i in range(5)]
        groups.reverse()

        self.expect(self.gtool.getGroupsByUserId(ANY)).result(groups)

        self.replay()

        executor = UsersSearchResultExecutor(self.context, '', True)
        result = executor.get_group_names_of_user('user')

        self.assertEquals(result, 'group0, group1, group2, group3, group4')

    def test_filter_groups(self):

        groups = [Group('group%s' % i) for i in range(5)]
        groups.append(Group('AuthenticatedUsers'))

        self.expect(self.gtool.getGroupsByUserId(ANY)).result(groups)

        self.replay()

        executor = UsersSearchResultExecutor(self.context, '', True)
        result = executor.get_group_names_of_user('invalid')

        self.assertEquals(result, 'group0, group1, group2, group3, group4')


class UserTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(UserTests, self).setUp()

        self.request = self.stub_request()

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

    def base_search_result_executor(self, query, result, users_factory=None):

        # List with users to display
        if not users_factory:
            users_factory = [User('user%s' % str(i/2)) for i in range(5)]

        self.member = self.stub()

        self.expect(self.gtool.getGroupsByUserId(ANY)).result([])
        self.expect(self.mtool.getMemberById(ANY)).result(self.member)
        self.expect(self.member.getProperty('email')).result('test@test.ch')
        # Factory returns the users
        factory = self.mocker.mock(count=False)
        self.expect(factory(ANY)).result(users_factory)
        self.mock_utility(
            factory,
            IUserManagementVocabularyFactory,
            'plone.principalsource.Users',
        )

        self.expect(
            self.mtool.getMemberInfo(ANY)).call(
            lambda x: x != 'broken' and {
                'fullname': '%s Fullname' % x,
                'username': '%s Username' % x} or None)

        self.replay()

        # Executes the query
        executor = UsersSearchResultExecutor(self.context, query, True)

        self.assertEquals(executor(), result)

    def test_query_no_filter_no_page_no_size(self):
        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 0,
            'current_page': 0,
        }
        result = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        self.base_search_result_executor(query, result)

    def test_broke_user(self):

        users_factory = [User('user%s' % str(i)) for i in range(5)]
        users_factory.insert(3, User('broken'))

        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 50,
            'current_page': 1,
        }
        result = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname',
             'login': 'user0', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user1 Fullname',
            'login': 'user1', 'userid': 'user1'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user2 Fullname',
             'login': 'user2', 'userid': 'user2'},
            {'counter': 5, 'groups': 'No Group', 'name': 'user3 Fullname',
             'login': 'user3', 'userid': 'user3'},
            {'counter': 6, 'groups': 'No Group', 'name': 'user4 Fullname',
             'login': 'user4', 'userid': 'user4'},
        ]
        self.base_search_result_executor(query, result, users_factory)

    def test_query_no_batching(self):

        query = {
            'filter_text': '',
            'batching': False,
            'pagesize': 50,
            'current_page': 1,
        }
        result = [
            {
                'counter': 1,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0',
            },
            {
                'counter': 2,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 5,
                'groups': 'No Group',
                'name': 'user2 Fullname',
                'login': 'user2',
                'userid': 'user2'
            },
        ]
        self.base_search_result_executor(query, result)

    def test_query_batching(self):
        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 2,
            'current_page': 1,
        }
        result = [
            {
                'counter': 1,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 2,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        self.base_search_result_executor(query, result)

    def test_query_batching_second_page(self):
        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 2,
            'current_page': 2,
        }
        result = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        self.base_search_result_executor(query, result)

    def test_query_filter_and_no_batching(self):
        query = {
            'filter_text': 'user1',
            'batching': False,
            'pagesize': 2,
            'current_page': 1,
        }
        result = [
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
        ]
        self.base_search_result_executor(query, result)

    def test_query_filter_and_batching(self):
        query = {
            'filter_text': 'user',
            'batching': True,
            'pagesize': 2,
            'current_page': 3,
        }
        result = [
            {
                'counter': 1,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 2,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 5,
                'groups': 'No Group',
                'name': 'user2 Fullname',
                'login': 'user2',
                'userid': 'user2'
            },
        ]
        self.base_search_result_executor(query, result)

    def test_query_bigger_pagesize(self):
        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 50,
            'current_page': 1,
        }
        result = [
            {
                'counter': 1,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 2,
                'groups': 'No Group',
                'name': 'user0 Fullname',
                'login': 'user0',
                'userid': 'user0'
            },
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'userid': 'user1'
            },
            {
                'counter': 5,
                'groups': 'No Group',
                'name': 'user2 Fullname',
                'login': 'user2',
                'userid': 'user2'
            },
        ]
        self.base_search_result_executor(query, result)

    def test_query_bigger_current_page(self):
        query = {
            'filter_text': '',
            'batching': True,
            'pagesize': 50,
            'current_page': 5,
        }
        result = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        self.base_search_result_executor(query, result)

    def test_query_no_result(self):
        query = {
            'filter_text': 'blabla',
            'batching': True,
            'pagesize': 2,
            'current_page': 1,
        }
        result = []
        self.base_search_result_executor(query, result)

    def test_email_not_login(self):

        users_factory = [User('user%s' % str(i/2)) for i in range(5)]

        self.member = self.stub()

        self.expect(self.gtool.getGroupsByUserId(ANY)).result([])
        self.expect(self.mtool.getMemberById(ANY)).result(self.member)
        self.expect(self.member.getProperty('email')).result('test@test.ch')
        # Factory returns the users
        factory = self.mocker.mock(count=False)
        self.expect(factory(ANY)).result(users_factory)
        self.mock_utility(
            factory,
            IUserManagementVocabularyFactory,
            'plone.principalsource.Users',
        )

        self.expect(
            self.mtool.getMemberInfo(ANY)).call(
            lambda x: x != 'broken' and {
                'fullname': '%s Fullname' % x,
                'username': '%s Username' % x} or None)

        self.replay()

        query = {
            'filter_text': 'user1',
            'batching': False,
            'pagesize': 2,
            'current_page': 1,
        }
        result = [
            {
                'counter': 3,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'email': 'test@test.ch',
                'userid': 'user1'
            },
            {
                'counter': 4,
                'groups': 'No Group',
                'name': 'user1 Fullname',
                'login': 'user1',
                'email': 'test@test.ch',
                'userid': 'user1'
            },
        ]

        executor = UsersSearchResultExecutor(self.context, query, False)

        self.assertEquals(executor(), result)


class User(object):
    """ Mockobject representing a user of the principal source
    """

    def __init__(self, id_):
        self.id = id_

    def get(self, attr):
        return self.id


class Group(object):
    """ Mockobject representing a group of the portal_groups utility
    """

    def __init__(self, title):
        self.title = title

    def getGroupTitleOrName(self):
        return self.title

    def getId(self):
        return self.title
