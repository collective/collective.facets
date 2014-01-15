__author__ = 'dylanjay'
# -*- coding: utf-8 -*-
from Acquisition import aq_inner

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from collective.facets.testing import \
    PLONEAPPCOLLECTION_INTEGRATION_TESTING
from collective.facets.testing import PLONEAPPCOLLECTION_FUNCTIONAL_TESTING

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, \
    TEST_USER_PASSWORD, setRoles, login

#from plone.app.collection.interfaces import ICollection
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


    def add_facet(self, index, name, title, desc='', _type='FieldType:StringField'):
        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')

        self.browser.getControl(name='__ac_name').value = TEST_USER_NAME
        self.browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='submit').click()

        # add a facet
        self.browser.getControl("Add").click()
        prefix = 'form.widgets.facets.%s.widgets'%index
        self.browser.getControl(name='%s.name'%prefix).value=name
        self.browser.getControl(name='%s.display_title'%prefix).value=title
        self.browser.getControl(name='%s.description'%prefix).value=desc
        self.browser.getControl('Save').click()

    def test_add_facet(self):

        self.add_facet(0, 'myfacet', 'My Facet', 'My Description')

        # make sure it saved right

        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')
        self.assertIn('My Facet', self.browser.contents)
        self.assertIn('My Description', self.browser.contents)



    def test_add_stringfield(self):
        self.add_facet(0, 'facet1', 'My Facet', _type="FieldType:StringField")

        #check it adds a field to any content
        self.browser.open( self.collection.absolute_url()+'/edit' )
        page = self.browser.contents
        self.assertIn('data-fieldname="facet_facet1"', page)
        self.browser.getControl(name="facet_facet1").value="myvalue"
        self.browser.getControl("Save")

        # check we can search
        self.browser.open( self.collection.absolute_url()+'/edit' )
        self.assertTrue('facet_facet1' in self.browser.getControl(name="addindex").options)
        #self.browser.getControl("MyFacet").select()
        #self.browser.getControl('Is').select()
        #self.browser.getControl('myvalue').select()

        # check we can show as metadata
        self.assertIn('facet_facet1', self.browser.getControl(name="customViewFields_options").options)


    def test_remove_facet(self):
        self.add_facet(0, 'facet1', 'My Facet', _type="FieldType:StringField")

        # now delete our facet
        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')
        self.browser.getControl(name="form.widgets.facets.0.remove").value = True
        self.browser.getControl('Remove selected').click()
        self.browser.getControl('Save').click()

        #check it removed the field from content
        self.browser.open( self.collection.absolute_url()+'/edit' )
        page = self.browser.contents
        self.assertNotIn('data-fieldname="facet_facet1"', page)

        # no longer an catalog index
        self.assertNotIn('facet_facet1', self.browser.getControl(name="addindex").options)

        # no longer metadata
        self.assertNotIn('facet_facet1', self.browser.getControl(name="customViewFields_options").options)




def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)