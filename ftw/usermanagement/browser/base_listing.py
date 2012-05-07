from ftw.tabbedview.browser.listing import ListingView
from ftw.table.basesource import BaseTableSource


class BaseListing(ListingView):
    """BaseListing View for a tab in the tabbedview"""

    def __call__(self):

        if self.table_options is None:
            self.table_options = {}

        self.update()
        return self.template()

    def get_base_query(self):
        return {}

class BaseManagementTableSource(BaseTableSource):

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
        return BaseSearchResultExecutor(self.config.context, query)()


class BaseSearchResultExecutor(object):
    """ Search and display groups
    """

    def __init__(self, context, query):
        self.context = context
        self.query = query

    def __call__(self):
        return self.get_results()

    def get_results(self):
        """ Return results as a dict
        """
        return {}