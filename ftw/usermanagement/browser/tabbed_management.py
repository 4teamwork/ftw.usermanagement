from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.usermanagement import user_management_factory as _


class ManagementTabbedView(TabbedView):
    """TabbedView for User/Groups management"""

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""

        translate = self.context.translate
        return [{'id':'users_management', 'class':'',
                'description': translate(_('msg_usersDescription',default='Users-management')),
                },
                {'id':'groups_management', 'class':'',
                'description': translate(_('msg_groupsDescription',default='Groups-management')),
                },
               ]
