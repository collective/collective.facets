
from plone.app.registry.browser import controlpanel

try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
    from z3c.form.browser.text import TextFieldWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget
    from plone.z3cform.text import TextFieldWidget
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from interfaces import IFacetSettings
from plone.registry.interfaces import IRegistry
from Products.Five import BrowserView

try:
    from plone.app.querystring.interfaces import IQueryField
except ImportError:
    IQueryField = None

from zope.i18nmessageid import MessageFactory
from utils import ComplexRecordsProxy, facetId
from Acquisition import aq_inner
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL


_ = MessageFactory('collective.facets')


def getRegistryFacets():
    reg = getUtility(IRegistry)
    proxy = ComplexRecordsProxy(reg, IFacetSettings,
                                prefix='collective.facets',
                                key_names={'facets': 'name'})
    return proxy


class FacetSettingsEditForm (controlpanel.RegistryEditForm):
    schema = IFacetSettings
    label = u"Facets Settings"
    description = u"Manage your additional facets. For adding field to " \
                  u"specifc types, use the Dexterity plugin"

    def getContent(self):
        return getRegistryFacets()

    def applyChanges(self, data):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        proxy = getRegistryFacets()
        cur_ids = set([facet.name for facet in proxy.facets])
        new_ids = set([facet.name for facet in data['facets']])

        delnames = cur_ids.difference(new_ids)

        for name in delnames:
            i = 0
            for facet in proxy.facets:
                if facet.name is name:
                    self.removeField(facet)
                    del proxy.facets[i]
                    break
                i += 1

        #i = 0
        #for facet in proxy.facets:
        #    if facet.name in delnames:
        #        self.removeField(facet)
        #        del proxy.facets[i]
        #    i += 1

        proxy.facets = data['facets']

        #indexes = self.catalog.indexes()
        indexables = []
        for facet in data['facets']:
            indexables.extend(self.addField(facet))
                #logger.info("Added %s for field %s.", 'KeywordIndex', name)
        if len(indexables) > 0:
            #logger.info("Indexing new indexes %s.", ', '.join(indexables))
            self.catalog.manage_reindexIndex(ids=indexables)

    def addField(self, facet):
        """add index, collection field etc"""

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
        fields = reg.collectionOfInterface(IQueryField,
                                           prefix='plone.app.querystring.field')
        # need to override prefix as default is field/
        fields.prefix = 'plone.app.querystring.field.'
        return fields


class FacetsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FacetSettingsEditForm

DOC_LANG = {'assyrian': 'ASY',
            'dari': 'DAR',
            'karen': 'KAR',
            'koori': 'KOO',
            'sorani': 'SOR',
            'sudanese': 'SUD',
            'tetum': 'TET',
            'tigrigna': 'TIR',
            'am': 'AMH',
            'ar': 'ARA',
            'bn': 'BEN',
            'bs': 'BSN',
            'cs': 'CZE',
            'de': 'GER',
            'din': 'DIN',
            'el': 'GRE',
            'en': 'ENG',
            'es': 'SPA',
            'fa': 'FAS',
            'fj': 'Fij',
            'fr': 'FRE',
            'hi': 'HIN',
            'hr': 'SCR',
            'hu': 'HUN',
            'hy': 'ARM',
            'id': 'IND',
            'it': 'ITA',
            'ja': 'JPN',
            'km': 'KHM',
            'ko': 'KOR',
            'ku': 'KUR',
            'lo': 'LAO',
            'mi': 'MAO',
            'mk': 'MAC',
            'ms': 'MAL',
            'mt': 'MLT',
            'my': 'BUR',
            'ne': 'NEP',
            'nl': 'DUT',
            'om': 'ORM',
            'pa': 'PAN',
            'pl': 'POL',
            'ps': 'PUS',
            'pt': 'POR',
            'rn': 'KIR',
            'ro': 'RUM',
            'ru': 'RUS',
            'si': 'SIN',
            'sm': 'SMO',
            'so': 'SOM',
            'sq': 'ALB',
            'sr': 'SCC',
            'sw': 'SWA',
            'ta': 'TAM',
            'th': 'THA',
            'tl': 'TGL',
            'to': 'TON',
            'tr': 'TUR',
            'uk': 'UKR',
            'ur': 'URD',
            'vi': 'VIE',
            'zh-hans': 'ZHO',
            'zh-hant': 'CHI'}

DOC_LANG_NAME = {'DIN': 'Dinka',
                 'SUD': 'Sudanese',
                 'BEN': 'Bengali',
                 'KOO': 'Koori',
                 'SWA': 'Swahili',
                 'SOM': 'Somali',
                 'KUR': 'Kurdish',
                 'TIR': 'Tigrigna',
                 'SMO': 'Samoan',
                 'TON': 'Tongan',
                 'Fij': 'Fijian',
                 'KOR': 'Korean',
                 'SIN': 'Sinhalese',
                 'ZHO': 'Chinese Simplified',
                 'AMH': 'Amharic',
                 'KAR': 'Karen',
                 'BUR': 'Burmese',
                 'FAS': 'Farsi',
                 'ASY': 'Assyrian',
                 'ENG': 'English',
                 'POR': 'Portuguese',
                 'POL': 'Polish',
                 'SCC': 'Serbian',
                 'MAL': 'Malay',
                 'PAN': 'Punjabi',
                 'BSN': 'Bosnian',
                 'SOR': 'Sorani',
                 'KHM': 'Khmer',
                 'DAR': 'Dari',
                 'SPA': 'Spanish',
                 'TET': 'Tetum',
                 'TGL': 'Filipino',
                 'SCR': 'Croatian',
                 'URD': 'Urdu',
                 'NEP': 'Nepalese',
                 'FRE': 'French',
                 'GER': 'German',
                 'CHI': 'Chinese Traditional',
                 'UKR': 'Ukrainian',
                 'GRE': 'Greek',
                 'MLT': 'Maltese',
                 'TAM': 'Tamil',
                 'DUT': 'Dutch',
                 'THA': 'Thai',
                 'LAO': 'Lao',
                 'VIE': 'Vietnamese',
                 'JPN': 'Japanese',
                 'KIR': 'Kirundi',
                 'TUR': 'Turkish',
                 'RUM': 'Romanian',
                 'ALB': 'Albanian',
                 'ITA': 'Italian',
                 'ARA': 'Arabic',
                 'MAC': 'Macedonian',
                 'ORM': 'Oromo',
                 'HIN': 'Hindi',
                 'HUN': 'Hungarian',
                 'IND': 'Indonesian',
                 'RUS': 'Russian',
                 'PUS': 'Pushto',
                 'ARM': 'Armenian',
                 'MAO': 'Maori',
                 'CZE': 'Czech'}


class FieldSwitcher(BrowserView):
    """View on an object to switch field data"""
    def run_task(self, **kwargs):
        context = aq_inner(self.context)
        #portal_languages = getToolByName(context, 'portal_languages', None)
        portal_vocabularies = getToolByName(context, ATVOCABULARYTOOL, None)
        language_vocabulary = getattr(portal_vocabularies,
                                      'mhcslanguagevocabulary', None)
        from_field = 'language'
        to_field = 'facet_mhcs_language'
        error_path = []
        if not from_field or not to_field:
            return "Not valid input"

        context_type = 'File'

        path = context.getPhysicalPath()
        path = '/'.join(path)

        if context_type:
            brains = context.portal_catalog(path={"query": path},
                                            portal_type=context_type)
        else:
            brains = context.portal_catalog(path={"query": path})

        for brain in brains:
            brain_context = brain.getObject()
            schema = brain.Schema()

            if from_field not in schema or to_field not in schema:
                #return "Not valid attribute"
                continue

            from_attribute = brain_context.Schema()[from_field].get(
                brain_context)
            to_attribute = brain_context.Schema()[to_field].get(brain_context)

            from_type = type(from_attribute)
            to_type = type(to_attribute)
            print "from: %s" % from_type
            print "to: %s" % to_type

            if from_field == 'language':
                from_attribute = from_attribute.lower()
                if from_attribute in DOC_LANG:
                    from_attribute = DOC_LANG[from_attribute]
                    language_name = DOC_LANG_NAME[from_attribute]
                    from_attribute = from_attribute.lower()
                #    language_name = portal_languages.getNameForLanguageCode(
                #        from_attribute)
                    # http://plone.org/documentation/kb/
                    # archgenxml-getting-started/vocabulary-manager
                    print "Language: %s %s" % (from_attribute, language_name)
                    language_vocabulary.addTerm(from_attribute, language_name,
                                                silentignore=True)
                else:
                    path = brain_context.getPhysicalPath()
                    language_from_filename = path[-1][:-4].split('-')[-1]
                    if language_from_filename in DOC_LANG_NAME:
                        from_attribute = language_from_filename.lower()
                        language_name = DOC_LANG_NAME[language_from_filename]
                        print "Language: %s %s" % (from_attribute,
                                                   language_name)
                        language_vocabulary.addTerm(from_attribute,
                                                    language_name,
                                                    silentignore=True)
                    else:
                        error_path.append('/'.join(brain_context.getPhysicalPath()))
                        continue

            # do the task
            if from_type != to_type:
                if from_type == str and to_type == tuple:
                    from_attribute = tuple([from_attribute])
                elif from_type == str and to_type == list:
                    from_attribute = [from_attribute]
                else:
                    #return NotImplemented
                    continue

            if to_attribute:
                print "before: %s" % to_attribute
            else:
                print "before: empty type of %s" % to_type
            #context.update(**{to_field: from_attribute})
            brain_context.Schema()[to_field].set(brain_context, from_attribute)
            brain_context.reindexObject(to_field)
            print "after: %s" % brain_context.Schema()[to_field].get(
                brain_context)

        return "complete %s" % error_path
