from zope.i18nmessageid import MessageFactory


user_management_factory = MessageFactory('ftw.usermanagement')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
