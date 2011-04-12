from ftw.tabbedview.browser.tabbed import TabbedView


class ManagementTabbedView(TabbedView):
    """TabbedView for User/Groups management"""

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""
        return [{'id':'users', 'class':''},
                {'id':'groups','class':''},
               ]
