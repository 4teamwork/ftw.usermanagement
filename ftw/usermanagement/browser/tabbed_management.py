from ftw.tabbedview.browser.tabbed import TabbedView


class ManagementTabbedView(TabbedView):
    """TabbedView for User/Groups management"""

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""
        return list((
            {'id': 'user_management',
             'url': 'user_management',
             'class': 'UserManagement', },
            {'id': 'group_management',
             'url': 'group_management',
             'class': 'GroupManagement', }))
