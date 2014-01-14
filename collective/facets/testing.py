import doctest

from zope.configuration import xmlconfig

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
import collective.facets

try:
    import plone.app.collection
    PLONE43 = True
except:
    PLONE43 = False



class PloneAppCollectionLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        if PLONE43:
            xmlconfig.file('configure.zcml', plone.app.collection,
                           context=configurationContext)
        xmlconfig.file('configure.zcml', collective.facets,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        if PLONE43:
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