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
