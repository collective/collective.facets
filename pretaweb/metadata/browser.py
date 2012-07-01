
from plone.app.registry.browser import controlpanel
try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
    from z3c.form.browser.text import TextFieldWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget
    from plone.z3cform.text import TextFieldWidget
    
from Products.CMFCore.utils import getToolByName
from interfaces import IMetadataSettings

class MetadataSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IMetadataSettings
    label = u"Metadata Settings"
    description = u"Settings to add your own metadata categories"


    def updateFields(self):
        super(MetadataSettingsEditForm, self).updateFields()
        self.fields['metadata'].widgetFactory = TextLinesFieldWidget


    def updateWidgets(self):
        super(MetadataSettingsEditForm, self).updateWidgets()
        self.widgets['metadata'].rows = 4
        self.widgets['metadata'].style = u'width: 30%;'

    def applyChanges(self, data):
        super(MetadataSettingsEditForm, self).applyChanges(data)
        catalog = getToolByName(self.context, 'portal_catalog')
        indexes = catalog.indexes()
        indexables = []
        for name in data['metadata']:
            if type(name) == type(u''):
                name = name.encode('utf-8')

            if name not in indexes:
                catalog.addIndex(name, 'KeywordIndex')
                indexables.append(name)
                #logger.info("Added %s for field %s.", 'KeywordIndex', name)
        if len(indexables) > 0:
            #logger.info("Indexing new indexes %s.", ', '.join(indexables))
            catalog.manage_reindexIndex(ids=indexables)



class MetadataSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MetadataSettingsEditForm


