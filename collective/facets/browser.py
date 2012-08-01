
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
from interfaces import IFacetSettings, IFacetDefinition, IFacetEditSettings
from plone.registry.interfaces import IRegistry
from plone.registry import field, Record
from plone.app.querystring.interfaces import IQueryField
from z3c.form import form, button
from zope.i18nmessageid import MessageFactory
from schema import implements

_ = MessageFactory('plone')

class FacetEditSettings(object):
    implements(IFacetEditSettings)


class FacetSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IFacetEditSettings
    label = u"Facets Settings"
    description = u"Manage your additional facets"

    def getContent(self):
        readonly = FacetEditSettings()
        reg = getUtility(IRegistry)
        # copy non-collection settings
        data = reg.forInterface(IFacetSettings, prefix='collective.facets')
        for name in data.__schema__:
            setattr(readonly, name, getattr(data, name))
        # switch out facet data for that from the registry
        facets = sorted(reg.collectionOfInterface(IFacetDefinition, prefix='facet').items())
        readonly.facets = [facet for _,facet in facets]
        return readonly

    def applyChanges(self, data):
        reg = getUtility(IRegistry)
        facets = reg.collectionOfInterface(IFacetDefinition, prefix='facet')

        #super(MetadataSettingsEditForm, self).applyChanges(data)
        self.catalog = getToolByName(self.context, 'portal_catalog')
        indexes = self.catalog.indexes()
        indexables = []
        #metadata = data['facets'] if data['facets'] else []
        for facet in data['facets']:
            name = facet.name
            if type(name) == type(u''):
                name = fname.encode('utf-8')
            if self.addfield(name):
                indexables.append( name )
                #logger.info("Added %s for field %s.", 'KeywordIndex', name)
        if len(indexables) > 0:
            #logger.info("Indexing new indexes %s.", ', '.join(indexables))
            self.catalog.manage_reindexIndex(ids=indexables)

        # remove indexes for unused fields

        #finally set the data in the registry
        i = 0
        for facet in data['facets']:
            facets['facet'+str(i)] = facet
            i += 1

        # remove any remaining fields
        for i in range(len(facets)-1,len(data['facets'])-1,-1):
            facet = facets['facet'+str(i)]
            name = facet.name
            if type(name) == type(u''):
                name = name.encode('utf-8')
            self.removeField(name)
            del facets['facet'+str(i)]


#    def updateFields(self):
#        super(MetadataSettingsEditForm, self).updateFields()
#        #self.fields['metadata'].widgetFactory = TextLinesFieldWidget
#
#
#    def updateWidgets(self):
#        super(MetadataSettingsEditForm, self).updateWidgets()
#        #self.widgets['metadata'].rows = 4
#        #self.widgets['metadata'].style = u'width: 30%;'


    def addfield(self, name, description=u""):
        "add index, collection field etc"

        collections = self.getCollectionMap()
        field = collections.setdefault(name)
        field.title = u"%s Tag" % name
        field.description = u"" + description
        field.group = u'Metadata'
        field.sortable = True
        field.enabled = True
        field.vocabulary = u'plone.app.vocabularies.Keywords'
        field.operations = ['plone.app.querystring.operation.selection.is']

        if name not in self.catalog.indexes():
            self.catalog.addIndex(name, 'KeywordIndex')
            return True

    def removeField(self, name):
        collections = self.getCollectionMap()
        if name in collections:
            del collections[name]
        if name in self.catalog.indexes():
            self.catalog.delIndex(name)

    def getCollectionMap(self):
        reg = getUtility(IRegistry)
        fields = reg.collectionOfInterface(IQueryField, prefix='plone.app.querystring.field')
        # need to override prefix as default is field/
        fields.prefix='plone.app.querystring.field.'
        return fields



class FacetsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FacetSettingsEditForm


