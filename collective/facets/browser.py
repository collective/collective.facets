
from plone.app.registry.browser import controlpanel

try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
    from z3c.form.browser.text import TextFieldWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget
    from plone.z3cform.text import TextFieldWidget
from zope.component import adapts, getUtility

from Products.CMFCore.utils import getToolByName
from interfaces import IFacetSettings
from plone.registry.interfaces import IRegistry
from plone.registry import field, Record
from plone.app.querystring.interfaces import IQueryField
from z3c.form import form, button
from zope.i18nmessageid import MessageFactory
from zope import schema
from schema import implements
from utils import ComplexRecordsProxy, facetId

_ = MessageFactory('plone')


class FacetSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IFacetSettings
    label = u"Facets Settings"
    description = u"Manage your additional facets"

    def getContent(self):
        reg = getUtility(IRegistry)
        return ComplexRecordsProxy(reg, IFacetSettings, prefix='collective.facets')

    def applyChanges(self, data):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        reg = getUtility(IRegistry)
        proxy = ComplexRecordsProxy(reg, IFacetSettings, prefix='collective.facets')
        cur_ids = set([f.name for f in proxy.facets])
        new_ids = set([f.name for f in data['facets']])

        delnames = cur_ids.difference(new_ids)
        i = 0
        for facet in proxy.facets:
            if facet.name in delnames:
                self.removeField(facet)
                del proxy.facets[i]
            i += 1

        proxy.facets = data['facets']

        indexes = self.catalog.indexes()
        indexables = []
        for facet in data['facets']:
            indexables.extend(self.addfield(facet))
                #logger.info("Added %s for field %s.", 'KeywordIndex', name)
        if len(indexables) > 0:
            #logger.info("Indexing new indexes %s.", ', '.join(indexables))
            self.catalog.manage_reindexIndex(ids=indexables)


#    def updateFields(self):
#        super(MetadataSettingsEditForm, self).updateFields()
#        #self.fields['metadata'].widgetFactory = TextLinesFieldWidget
#
#
#    def updateWidgets(self):
#        super(MetadataSettingsEditForm, self).updateWidgets()
#        #self.widgets['metadata'].rows = 4
#        #self.widgets['metadata'].style = u'width: 30%;'


    def addfield(self, facet):
        "add index, collection field etc"

        id = facetId(facet.name)
        collections = self.getCollectionMap()
        field = collections.setdefault(id)
        field.title = u"%s" % facet.name
        field.description = u"" + facet.description
        field.group = u'Metadata'
        field.sortable = True
        field.enabled = True
        field.vocabulary = u'plone.app.vocabularies.Keywords'
        field.operations = ['plone.app.querystring.operation.selection.is']

        if id not in self.catalog.indexes():
            self.catalog.addIndex(id, 'KeywordIndex')
            return [id]
        else:
            return []

    def removeField(self, facet):
        collections = self.getCollectionMap()
        id = facetId(facet.name)
        if id in collections:
            del collections[id]
        if id in self.catalog.indexes():
            self.catalog.delIndex(id)

    def getCollectionMap(self):
        reg = getUtility(IRegistry)
        fields = reg.collectionOfInterface(IQueryField, prefix='plone.app.querystring.field')
        # need to override prefix as default is field/
        fields.prefix='plone.app.querystring.field.'
        return fields



class FacetsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FacetSettingsEditForm


