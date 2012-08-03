import doctest

from zope.configuration import xmlconfig

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
import collective.facets


class PloneAppCollectionLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import plone.app.collection
        xmlconfig.file('configure.zcml', plone.app.collection,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', collective.facets,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.collection:default')
        applyProfile(portal, 'collective.facets:default')


PLONEAPPCOLLECTION_FIXTURE = PloneAppCollectionLayer()

PLONEAPPCOLLECTION_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Integration")
PLONEAPPCOLLECTION_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(PLONEAPPCOLLECTION_FIXTURE,),
    name="PloneAppCollectionLayer:Functional")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)