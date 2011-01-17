from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager


class IFtwUserManagement(IDefaultPloneLayer):
    """Marker interface for a zope 3 browser layer.
    """
    
class IBeforTablerManager(IViewletManager):
    """ViewletManager for Viewlets"""
    