from plone.theme.interfaces import IDefaultPloneLayer
from zope.schema.interfaces import IVocabularyFactory


class IFtwUserManagement(IDefaultPloneLayer):
    """ Marker interface for a zope 3 browser layer.
    """


class IUserManagementVocabularyFactory(IVocabularyFactory):
    """ Vocabulary returning groups or users
    """
