__author__ = 'dylanjay'
# -*- coding: utf-8 -*-
from Acquisition import aq_inner

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from collective.facets.testing import \
    PLONEAPPCOLLECTION_INTEGRATION_TESTING
from collective.facets.testing import \
    PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, setRoles, login

from plone.app.collection.interfaces import ICollection
from plone.testing.z2 import Browser


query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]

#query = [{
#    'i': 'SearchableText',
#    'o': 'plone.app.querystring.operation.string.contains',
#    'v': 'Autoren'
#}]

class PloneAppCollectionViewsIntegrationTest(unittest.TestCase):

    layer = PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Collection',
                                  'collection1')
        self.collection = aq_inner(self.folder['collection1'])

        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        self.browser = Browser(self.portal)
        portalURL = self.portal.absolute_url()
        self.browser.open(portalURL)

        self.request.set('URL', self.collection.absolute_url())
        self.request.set('ACTUAL_URL', self.collection.absolute_url())

    def test_addfacet(self):
        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')

        self.browser.getControl(name='__ac_name').value = TEST_USER_NAME
        self.browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='submit').click()

        # add a facet 
        self.browser.getControl("Add").click()
        self.browser.getControl(name='form.widgets.facets.0.widgets.name').value="MyFacet"
        self.browser.getControl(name='form.widgets.facets.0.widgets.description').value="My Description"
        self.browser.getControl('Save').click()

        #check it adds a field to any content
        self.browser.open( self.collection.absolute_url()+'/edit' )
        self.browser.getControl("myfacet_keywords:lines").value="myvalue"
        self.browser.getControl("Save")

        # check we can search
        self.browser.open( self.collection.absolute_url()+'/edit' )
        self.browser.getControl("Add criterion")
        self.browser.getControl("MyFacet").select()
        self.browser.getControl('Is').select()
        self.browser.getControl('myvalue').select()



#        view = self.collection.restrictedTraverse('@@view')
#        self.assertTrue(view())
#        self.assertEquals(view.request.response.status, 200)




def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)