from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.testing import Layer
from plone.testing import zca
from plone.testing.z2 import installProduct
from zope.configuration import xmlconfig


class UsermanagementZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

    def testTearDown(self):
        del self['configurationContext']


USERMANAGEMENT_ZCML_LAYER = UsermanagementZCMLLayer()


class UsermanagementPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.usermanagement
        xmlconfig.file(
            'configure.zcml', ftw.usermanagement, context=configurationContext)
        installProduct(app, 'ftw.usermanagement')

        import ftw.tabbedview
        xmlconfig.file(
            'configure.zcml', ftw.tabbedview, context=configurationContext)
        installProduct(app, 'ftw.tabbedview')

        import ftw.table
        xmlconfig.file(
            'configure.zcml', ftw.table, context=configurationContext)
        installProduct(app, 'ftw.table')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.usermanagement:default')
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.table:default')

UsermanagementPloneFixture = UsermanagementPloneLayer()
USERMANAGEMENT_PLONE_LAYER = IntegrationTesting(
    bases=(UsermanagementPloneFixture, ),
    name="ftw.usermanagement:Integration")
