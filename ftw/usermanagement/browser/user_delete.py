from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class UserDelete(BrowserView): 
    """Get a list of users from REQUEST to delete"""
    
    template = ViewPageTemplateFile('user_delete.pt')
    
    def __call__(self):
        return self.template()