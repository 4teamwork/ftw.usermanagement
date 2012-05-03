from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig


class UsermanagementZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))
        config = self['configurationContext']

    def testTearDown(self):
        del self['configurationContext']


USERMANAGEMENT_ZCML_LAYER = UsermanagementZCMLLayer()
