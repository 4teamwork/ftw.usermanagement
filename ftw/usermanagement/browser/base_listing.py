from ftw.tabbedview.browser.listing import ListingView


class BaseListing(ListingView):
    """BaseListing View for a tab in the tabbedview"""

    def __call__(self):

        if self.table_options is None:
            self.table_options = {}

        self.update()
        return self.template()

    def get_base_query(self):
        query = []
        return query

    def _custom_sort_method(self, results, sort_on, sort_reverse):
        """Sort the columns in ftw.table"""

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
