from ftw.testing import MockTestCase
from ftw.usermanagement.testing import USERMANAGEMENT_ZCML_LAYER
from ftw.usermanagement.browser.base_listing import BaseManagementTableSource


class BaseManagementTableSourceTests(MockTestCase):

    layer = USERMANAGEMENT_ZCML_LAYER

    def setUp(self):
        super(BaseManagementTableSourceTests, self).setUp()

        self.request = {}
        self.config = self.mocker.mock(count=False)

    def test_validate_base_query_valid(self):

        source = BaseManagementTableSource(self.config, self.request)
        self.replay()

        result = source.validate_base_query({'query': 'valid'})

        self.assertEquals(result, {'query': 'valid'})

    def test_validate_base_query_invalid(self):

        source = BaseManagementTableSource(self.config, self.request)
        self.replay()

        self.assertRaises(
            ValueError,
            source.validate_base_query,
            ['query'])

    def test_extend_query_with_ordering(self):

        source = BaseManagementTableSource(self.config, self.request)
        self.replay()

        result = source.extend_query_with_ordering({'query': 'valid'})

        self.assertEquals(result, {'query': 'valid'})

    def test_extend_query_with_textfilter(self):

        source = BaseManagementTableSource(self.config, self.request)
        self.replay()

        result = source.extend_query_with_textfilter({}, 'filter text')

        self.assertEquals(result, {'filter_text': 'filter text'})

    def test_extend_query_with_batching(self):

        self.expect(self.config.batching_enabled).result(True)
        self.expect(self.config.lazy).result(False)
        self.expect(self.config.batching_pagesize).result(3)
        self.expect(self.config.batching_current_page).result(4)

        source = BaseManagementTableSource(self.config, self.request)

        self.replay()

        result = source.extend_query_with_batching({})

        self.assertEquals(
            result,
            {
                'pagesize': 3,
                'current_page': 4,
                'batching': True,
            })

    def test_extend_query_with_batching_is_lazy(self):

        self.expect(self.config.batching_enabled).result(True)
        self.expect(self.config.lazy).result(True)

        source = BaseManagementTableSource(self.config, self.request)

        self.replay()

        result = source.extend_query_with_batching({})

        self.assertEquals(result, {'batching': False})

    def test_extend_query_with_batching_no_batching(self):

        self.expect(self.config.batching_enabled).result(False)
        self.expect(self.config.lazy).result(False)

        source = BaseManagementTableSource(self.config, self.request)

        self.replay()

        result = source.extend_query_with_batching({})

        self.assertEquals(result, {'batching': False})
