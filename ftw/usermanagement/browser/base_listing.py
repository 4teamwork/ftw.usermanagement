from ftw.tabbedview.browser.listing import ListingView
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements
from ftw.table.basesource import BaseTableSource


class IUsersSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""


class BaseListing(ListingView):

    implements(IUsersSourceConfig)

    def __call__(self):

        self.update()
        return self.template()

    def get_base_query(self):
        query = self.users()
        return query


    def _custom_sort_method(self, results, sort_on, sort_reverse):

        results.sort(
            lambda x, y: cmp(
                str(x.get(sort_on, '')).lower(),
                str(y.get(sort_on, '')).lower()))
        if sort_reverse:
            results.reverse()

        #add static numbers
        for index, result in enumerate(results):
            result['counter'] = index + 1

        return results

class UsersTableSource(BaseTableSource):

    def validate_base_query(self, query):
        return query

    def search_results(self, results):

        search = self.config.filter_text.lower()

        if search:

            def filter_(item):
                searchable = ' '.join((item['name'], item['email'])).lower()
                return search in searchable
            return filter(filter_, results)
        return results
