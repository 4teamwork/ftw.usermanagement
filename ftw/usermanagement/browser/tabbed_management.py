from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.usermanagement import user_management_factory as _
from zope.interface import implements
from ftw.tabbedview.interfaces import INoExtJS


class ManagementTabbedView(TabbedView):
    """TabbedView for User/Groups management"""

    implements(INoExtJS)

    def __init__(self, context, request):
        super(ManagementTabbedView, self).__init__(context, request)

        if not request.get('disable_border'):
            request.set('disable_border', '1')

        request.set('disable_plone.rightcolumn', True)
        request.set('disable_plone.leftcolumn', True)

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""

        translate = self.context.translate
        return [
            {
                'id': 'users_management',
                'class': '',
                'description': translate(
                    _('msg_usersDescription',
                      default='Users-management')),
            },

            {
                'id': 'groups_management',
                'class': '',
                'description': translate(
                    _('msg_groupsDescription',
                      default='Groups-management')),
            }]
