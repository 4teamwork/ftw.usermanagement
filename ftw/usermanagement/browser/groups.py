from ftw.table.interfaces import ITableGenerator
from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryMultiAdapter, queryUtility



class GroupManagement(BrowserView):
    """
    A ftw.table based user management view
    """

    columns = (
        {'column': 'group_title',
         'column_title': _(u'label_group_title', default='Title'), },
        {'column': 'group_id',
         'column_title': _(u'label_group_id', default='Id'), },
        {'column': 'group_members',
         'column_title': _(u'label_group_members', default='Members'), },)


    template = ViewPageTemplateFile('groups.pt')


    def __call__(self):
        if self.request.get('add.group', ''):
            return self.create_group()
        return self.template()

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.gtool = getToolByName(self, 'portal_groups')

        self.groupprefs = queryMultiAdapter((context, request),
                                         name=u'usergroup-groupprefs')
        
        
    def render_table(self):
        """Renders a table usfing ftw.table"""

        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.groups, self.columns, sortable = True)

    @property
    def groups(self):
        groups = self.groupprefs.doSearch(searchString='')
        results = []
        for g in groups:
            if 'AuthenticatedUsers' != g['groupid']:
                results.append(dict(
                    group_id=g['groupid'],
                    group_title=g['title'],
                    group_members=''))
        return results
        


    def create_group(self):
        """Validates input and creates a new group"""
        
        # XXX: Validate input
        group_id = self.request.get('group_id', '')
        group_title = self.request.get('group_title', group_id)
        
        if group_id:
            data = dict(title=group_title)
            success = self.gtool.addGroup(group_id, **data)
            if not success:
                # reset group_id
                group_id = ''
        
        if group_id:
            # Successfully created group
            msg = _(u'text_group_created')
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type="info")
        else:
            msg = _(u'text_enter_valid_group_id')
            IStatusMessage(self.request).addStatusMessage(
                msg,
                type="error")
        return self.template()
        