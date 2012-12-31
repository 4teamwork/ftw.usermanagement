from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class UserNotify(BrowserView):

    template = ViewPageTemplateFile("notify_user_html.pt")

    def __call__(self, **kwargs):
        acl_users = getToolByName(self.context, 'acl_users')
        user = acl_users.getUserById(kwargs['username'])
        self.username = user.getUserName()
        return self.template(**kwargs)
