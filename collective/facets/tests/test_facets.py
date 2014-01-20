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
from plone.testing.z2 import Browser

try:
    from plone.app.collection.interfaces import ICollection
    PLONE43 = True
except:
    PLONE43 = False


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

        self.folder.invokeFactory('Document', 'test-page')
        self.page = self.folder['test-page']
        self.page.setTitle('My Page')
        if PLONE43:

            self.folder.invokeFactory('Collection',
                                      'collection1',
                                      'My Collection')
        else:
            self.folder.invokeFactory('Topic',
                                      'collection1',
                                      'My Collection')

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
        #print self.browser.getControl(name='%s.vocabularies:list'%prefix).options
        self.browser.getControl(name='%s.vocabularies:list'%prefix).value=[_type]
        self.browser.getControl('Save').click()

    def set_collection(self, facet_name, value):

        if PLONE43:
            query = [{
                'i': facet_name,
                'o': 'plone.app.querystring.operation.string.is',
                'v': value,
            }]

            self.collection.setQuery(query)
            self.assertEqual(len(self.collection.results()), 1)
            self.collection.setCustomViewFields([facet_name, 'Title'])
            self.collection.setLayout('tabular_view')
        else:
            topic = self.collection
            topic.addCriterion( facet_name, 'ATSimpleStringCriterion' )
            topic.getCriterion( '%s_ATSimpleStringCriterion'%facet_name ).setValue( value )
            topic.setCustomView(True)
            topic.setCustomViewFields([facet_name, 'Title'])

        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        self.browser.open( self.collection.absolute_url() )
        self.assertEquals(str(self.browser.getLink('My Page')),
                          "<Link text='My Page' url='http://nohost/plone/test-folder/test-page'>")
        self.assertIn(value, self.browser.contents)

#        self.browser.open( self.collection.absolute_url()+'/edit' )
#        self.assertTrue('facet_facet1' in self.browser.getControl(name="addindex").options)
        #self.browser.getControl("MyFacet").select()
        #self.browser.getControl('Is').select()
        #self.browser.getControl('myvalue').select()

        # check we can show as metadata
#        self.assertIn('facet_facet1', self.browser.getControl(name="customViewFields_options").options)


    def test_add_facet(self):

        self.add_facet(0, 'myfacet', 'My Facet', 'My Description')

        # make sure it saved right

        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')
        self.assertIn('My Facet', self.browser.contents)
        self.assertIn('My Description', self.browser.contents)

    def test_add_stringfield(self):
        self.add_facet(0, 'facet1', 'My Facet')

        #check it adds a field to a page
        self.browser.open( self.page.absolute_url()+'/edit' )
        self.browser.getControl(name="facet_facet1").value="myvalue"
        self.browser.getControl("Save").click()
        self.assertIn('Changes saved.', self.browser.contents)

        # check we can search and show metadata
        self.set_collection('facet_facet1', 'myvalue')



    def test_add_keywordfield(self):
        self.add_facet(0, 'facet1', 'My Facet', _type='FieldType:KeywordField')

        #check it adds a field to any content
        self.browser.open( self.page.absolute_url()+'/edit' )
        self.browser.getControl(name="facet_facet1_keywords:lines").value="myvalue\nyourvalue"
        self.browser.getControl("Save").click()

        # check we can search and show metadata
        self.set_collection('facet_facet1', 'myvalue')


    def test_add_vocabularyfield(self):
        self.add_facet(0, 'facet1', 'My Facet', _type='Group Ids')

        #check it adds a field to any content
        #self.browser.open( self.page.absolute_url()+'/edit' )
        #print self.browser.contents
        #print self.browser.getControl(name="facet_facet1_options").options
        #self.browser.getControl(name="facet_facet1:list").value=["Administrators"]
        #self.browser.getControl("Save").click()
        self.page.update(facet_facet1=['Administrators'])
        import transaction; transaction.commit()


        self.set_collection('facet_facet1', 'Administrators')

    def test_remove_facet(self):
        self.add_facet(0, 'facet1', 'My Facet')

        # now delete our facet
        self.browser.open(self.portal.absolute_url()+'/@@facets-settings')
        self.browser.getControl(name="form.widgets.facets.0.remove").value = True
        self.browser.getControl('Remove selected').click()
        self.browser.getControl('Save').click()

        #check it removed the field from content
        self.browser.open( self.page.absolute_url()+'/edit' )
        self.assertNotIn("facet_facet1", self.browser.contents)

        self.browser.open( self.collection.absolute_url()+'/edit' )
        # no longer an catalog index
        if PLONE43:
            self.assertNotIn('facet_facet1', self.browser.getControl(name="addindex").options)

        # no longer metadata
        self.assertNotIn('facet_facet1', self.browser.getControl(name="customViewFields_options").options)




def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)