
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
from interfaces import IFacetSettings, IFacetDefinition
from plone.registry.interfaces import IRegistry
from plone.registry import field, Record
from plone.app.querystring.interfaces import IQueryField
from z3c.form import form, button
from zope.i18nmessageid import MessageFactory
from schema import implements

_ = MessageFactory('plone')

class FacetSettings(object):
    implements(IFacetSettings)


class MetadataSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IFacetSettings
    label = u"Metadata Settings"
    description = u"Settings to add your own metadata categories"

    def getContent(self):
        readonly = FacetSettings()
        reg = getUtility(IRegistry)
        data = reg.forInterface(self.schema, prefix=self.schema_prefix)
        for name in data.__schema__:
            setattr(readonly, name, getattr(data, name))
        # switch out collection for
        facets = sorted(reg.collectionOfInterface(IFacetDefinition, prefix='facet').items())
        readonly.facets = [facet for _,facet in facets]
        return readonly


    def updateFields(self):
        super(MetadataSettingsEditForm, self).updateFields()
        #self.fields['metadata'].widgetFactory = TextLinesFieldWidget


    def updateWidgets(self):
        super(MetadataSettingsEditForm, self).updateWidgets()
        #self.widgets['metadata'].rows = 4
        #self.widgets['metadata'].style = u'width: 30%;'

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



    def addfield(self, name):
        "add index, collection field etc"

        #plone app querystring field Subject description	Description		Text	Tags are used for organization of content
        #plone app querystring field Subject enabled	Enabled		Bool	True
        #plone app querystring field Subject group	Group		TextLine	Text
        #plone app querystring field Subject operations	Operations		List	['plone.app.querystring.operation.selection.is']
        #plone app querystring field Subject sortable	Sortable		Bool	True
        #plone app querystring field Subject title	Title		TextLine	Tag
        #plone app querystring field Subject vocabulary	Vocabulary		TextLine	plone.app.vocabularies.Keywords

        reg = getUtility(IRegistry)
        fields = reg.collectionOfInterface(IQueryField, prefix='plone.app.querystring.field')
        fields.prefix='plone.app.querystring.field.'
        #reg.registerInterface(, prefix="plone.app.querystring.field.%s" % name)
        #field = reg.forInterface(IQueryField, prefix="plone.app.querystring.field.%s" % name)
        field = fields.setdefault(name)
        field.title = u"%s Tag" % name
        field.description = u""
        field.group = u'Text'
        field.sortable = True
        field.vocabulary = u'plone.app.vocabularies.Keywords'
        field.operations = ['plone.app.querystring.operation.selection.is']

        if name not in self.catalog.indexes():
            self.catalog.addIndex(name, 'KeywordIndex')
            return True

    def removeField(self, name):
        reg = getUtility(IRegistry)
        key = "plone.app.querystring.field.%s" % name
        if key in reg:
            del reg[key]
        if name in self.catalog.indexes():
            self.catalog.delIndex(name)


class MetadataSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MetadataSettingsEditForm


