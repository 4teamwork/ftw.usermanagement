from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
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

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        installProduct(app, 'ftw.usermanagement')
        installProduct(app, 'ftw.table')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.usermanagement:default')


UsermanagementPloneFixture = UsermanagementPloneLayer()
USERMANAGEMENT_FUNCTIONAL = FunctionalTesting(
    bases=(UsermanagementPloneFixture,
           set_builder_session_factory(functional_session_factory)),
    name='ftw.usermanagement:functional')
USERMANAGEMENT_PLONE_LAYER = IntegrationTesting(
    bases=(UsermanagementPloneFixture, ),
    name="ftw.usermanagement:Integration")
