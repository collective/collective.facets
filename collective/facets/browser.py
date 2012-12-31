
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

try:
    from plone.app.querystring.interfaces import IQueryField
except ImportError:
    IQueryField = None

from z3c.form import form, button
from zope.i18nmessageid import MessageFactory
from zope import schema
from schema import implements
from utils import ComplexRecordsProxy, facetId

_ = MessageFactory('collective.facets')


class FacetSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IFacetSettings
    label = u"Facets Settings"
    description = u"Manage your additional facets. For adding field to specifc types, use the Dexterity plugin"

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

        # new collections
        collections = self.getCollectionMap()
        if collections:
            field = collections.setdefault(id)
            field.title = u"%s" % facet.name
            field.description = u"" + facet.description
            field.group = u'Metadata'
            field.sortable = True
            field.enabled = True
            field.vocabulary = u'plone.app.vocabularies.Keywords'
            field.operations = ['plone.app.querystring.operation.selection.is']

        # old collections
        atct = getToolByName(self.context, 'portal_atct')
        atct.addIndex(id, facet.name, facet.description, enabled=True)
        atct.addMetadata(id, facet.name, facet.description, enabled=True)

        # catalog metadata
        if id not in self.catalog.schema():
            self.catalog.manage_addColumn(id)

        # catalog indexes
        if id not in self.catalog.indexes():
            self.catalog.addIndex(id, 'KeywordIndex')
            return [id]
        else:
            return []

    def removeField(self, facet):
        id = facetId(facet.name)

        collections = self.getCollectionMap()
        if collections and id in collections:
            del collections[id]

        # old collections
        atct = getToolByName(self.context, 'portal_atct')
        atct.removeIndex(id)
        atct.removeMetadata(id)

        if id in self.catalog.indexes():
            self.catalog.delIndex(id)
        if id in self.catalog.schema():
            self.catalog.manage_delColumn(id)

    def getCollectionMap(self):
        if not IQueryField:
            # IQueryField only available after Plone 4.2
            return None

        reg = getUtility(IRegistry)
        fields = reg.collectionOfInterface(IQueryField, prefix='plone.app.querystring.field')
        # need to override prefix as default is field/
        fields.prefix='plone.app.querystring.field.'
        return fields



class FacetsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FacetSettingsEditForm


