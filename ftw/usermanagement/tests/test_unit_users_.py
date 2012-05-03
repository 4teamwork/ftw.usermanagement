from ftw.testing import MockTestCase
from mocker import ANY
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.user.users import SearchResultExecutor
from ftw.usermanagement.interfaces import IUserManagementVocabularyFactory



class UserClasses(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(UserClasses, self).setUp()

        self.request = self.stub_request()

        self.context = self.stub()
        self.expect(self.context.REQUEST).result(self.request)

        self.mtool = self.mocker.mock(count=False)
        self.mock_tool(self.mtool, 'portal_membership')

        self.gtool = self.mocker.mock(count=False)
        self.mock_tool(self.gtool, 'portal_groups')

    def test_groups_by_user(self):
        """ Test the GroupsByUser class
        """

        # Normal groups
        groups_valid = [Group('group%s' % i) for i in range(5)]

        # No groups
        groups_invalid = []

        # Unsorted groups
        groups_unsorted = [Group('group%s' % i) for i in range(5)]
        groups_unsorted.reverse()

        # A group contains a id we don't want
        groups_filter = [Group('group%s' % i) for i in range(5)]
        groups_filter.append(Group('AuthenticatedUsers'))

        self.expect(self.gtool.getGroupsByUserId('valid')).result(groups_valid)
        self.expect(self.gtool.getGroupsByUserId('invalid')).result(groups_invalid)
        self.expect(self.gtool.getGroupsByUserId('unsorted')).result(groups_unsorted)
        self.expect(self.gtool.getGroupsByUserId('filter')).result(groups_filter)

        self.replay()

        executor = SearchResultExecutor(self.context, '')

        groups_valid = executor.get_group_names_of_user('valid')
        groups_invalid  = executor.get_group_names_of_user('invalid')
        groups_unsorted = executor.get_group_names_of_user('unsorted')
        groups_filter = executor.get_group_names_of_user('filter')

        self.assertEquals(groups_valid, 'group0, group1, group2, group3, group4')
        self.assertEquals(groups_invalid, 'No Group')
        self.assertEquals(groups_unsorted, 'group0, group1, group2, group3, group4')
        self.assertEquals(groups_filter, 'group0, group1, group2, group3, group4')

    def test_search_result_executor(self):

        # List with users to display
        users_factory = [User('user%s' % str(i/2)) for i in range(5)]

        self.expect(self.gtool.getGroupsByUserId(ANY)).result([])

        # Factory returns the users
        factory = self.mocker.mock(count=False)
        self.expect(factory(ANY)).result(users_factory)
        self.mock_utility(factory, IUserManagementVocabularyFactory, 'plone.principalsource.Users')

        self.expect(self.mtool.getMemberInfo(ANY)).call(lambda x: {'fullname': '%s Fullname' % x, 'username': '%s Username' % x})

        query_no_filter_no_page_no_size = {
            'filter_text': '',
            'batching': True,
            'pagesize': 0,
            'current_page': 0,
        }
        query_no_batching = {
            'filter_text': '',
            'batching': False,
            'pagesize': 50,
            'current_page': 1,
        }
        query_batching = {
            'filter_text': '',
            'batching': True,
            'pagesize': 2,
            'current_page': 1,
        }
        query_batching_second_page = {
            'filter_text': '',
            'batching': True,
            'pagesize': 2,
            'current_page': 2,
        }
        query_filter_and_no_batching = {
            'filter_text': 'user1',
            'batching': False,
            'pagesize': 2,
            'current_page': 1,
        }
        query_filter_and_batching = {
            'filter_text': 'user',
            'batching': True,
            'pagesize': 2,
            'current_page': 3,
        }
        query_bigger_pagesize = {
            'filter_text': '',
            'batching': True,
            'pagesize': 50,
            'current_page': 1,
        }
        query_bigger_current_page = {
            'filter_text': '',
            'batching': True,
            'pagesize': 50,
            'current_page': 5,
        }
        query_no_result = {
            'filter_text': 'blabla',
            'batching': True,
            'pagesize': 2,
            'current_page': 1,
        }

        self.replay()

        # Executes the query
        no_filter_no_page_no_size = SearchResultExecutor(self.context, query_no_filter_no_page_no_size)()
        no_batching = SearchResultExecutor(self.context, query_no_batching)()
        batching = SearchResultExecutor(self.context, query_batching)()
        batching_second_page = SearchResultExecutor(self.context, query_batching_second_page)()
        filter_and_no_batching = SearchResultExecutor(self.context, query_filter_and_no_batching)()
        filter_and_batching = SearchResultExecutor(self.context, query_filter_and_batching)()
        bigger_pagesize = SearchResultExecutor(self.context, query_bigger_pagesize)()
        bigger_current_page = SearchResultExecutor(self.context, query_bigger_current_page)()
        no_result = SearchResultExecutor(self.context, query_no_result)()

        result_no_filter_no_page_no_size = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 5, 'groups': 'No Group', 'name': 'user2 Fullname', 'userid': 'user2'},
        ]
        result_no_batching = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 5, 'groups': 'No Group', 'name': 'user2 Fullname', 'userid': 'user2'},
        ]
        result_batching = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        result_batching_second_page = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        result_filter_and_no_batching = [
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},

        ]
        result_filter_and_batching = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 5, 'groups': 'No Group', 'name': 'user2 Fullname', 'userid': 'user2'},
        ]
        result_bigger_pagesize = [
            {'counter': 1, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 2, 'groups': 'No Group', 'name': 'user0 Fullname', 'userid': 'user0'},
            {'counter': 3, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 4, 'groups': 'No Group', 'name': 'user1 Fullname', 'userid': 'user1'},
            {'counter': 5, 'groups': 'No Group', 'name': 'user2 Fullname', 'userid': 'user2'},
        ]
        result_bigger_current_page = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        result_no_filter_no_page_no_size = [
            {'counter': 1, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 2, 'groups': '', 'name': '', 'userid': 'user0'},
            {'counter': 3, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 4, 'groups': '', 'name': '', 'userid': 'user1'},
            {'counter': 5, 'groups': '', 'name': '', 'userid': 'user2'},
        ]
        result_no_result = []

        self.assertEquals(no_filter_no_page_no_size, result_no_filter_no_page_no_size)
        self.assertEquals(no_batching, result_no_batching)
        self.assertEquals(batching, result_batching)
        self.assertEquals(batching_second_page, result_batching_second_page)
        self.assertEquals(filter_and_no_batching, result_filter_and_no_batching)
        self.assertEquals(filter_and_batching, result_filter_and_batching)
        self.assertEquals(bigger_pagesize, result_bigger_pagesize)
        self.assertEquals(bigger_current_page, result_bigger_current_page)
        self.assertEquals(no_filter_no_page_no_size, result_no_filter_no_page_no_size)
        self.assertEquals(no_result, result_no_result)


class User(object):
    """ Mockobject representing a user of the principal source
    """
    def __init__(self, id):
        self.id = id

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
