from zope.component import adapts
from zope.interface import implements

from Products.Archetypes.public import KeywordWidget, InAndOutWidget, StringWidget
from Products.Archetypes import public as atapi
from Products.Archetypes.interfaces import IBaseContent

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender, \
    IBrowserLayerAwareExtender

from utils import facetId
from browser import getRegistryFacets

from collective.facets.interfaces import IAddOnInstalled
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError

class ExtensionStringField(ExtensionField, atapi.StringField):
    """ facets TextField
    """

class ExtensionKeywordField(ExtensionField, atapi.LinesField):
    """ Retrofitted keyword field """

    def Vocabulary(self, content_instance=None):
        vocab_name = self.vocabulary

        if not (isinstance(vocab_name, basestring) and vocab_name):
            return atapi.DisplayList()

        if vocab_name == 'FieldType:KeywordField':
            return atapi.DisplayList()

        pv = getToolByName(content_instance, 'portal_vocabularies', None)
        vocab = getattr(pv, vocab_name, None)
        if vocab:
            return vocab.getDisplayList(vocab)

        # refer to eea.facetednavigation.widgets.widget portal_vocabulary()
        voc = queryUtility(IVocabularyFactory, vocab_name, None)
        if voc:
            return atapi.DisplayList([(term.value,
                                       (term.title or term.token or term.value))
                                      for term in voc(content_instance)])
        return atapi.DisplayList()


class FacetsExtender(object):
    """Add a series of "facets" or categorisation fields to a type"""
    adapts(IBaseContent)
    # This extender will apply to all Archetypes based content

    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    # We use both orderable and browser layer aware sensitive properties

    # Don't do schema extending unless our add-on product is installed on
    # Plone site
    layer = IAddOnInstalled

    #NOTE: These methods are called quite frequently, so it pays to optimise
    #them. # https://osha.europa.eu/
    # https://code.gocept.com/svn/osha/OSHA/trunk/adapter/oshcontent.py

    def __init__(self, context):
        self.context = context

        try:
            proxy = getRegistryFacets()
        except ComponentLookupError:
            # not installed
            return

        self.fields = []
        for facet in proxy.facets:
            field_name = facetId(facet.name)
            vocabularies = facet.vocabularies

            if vocabularies == 'FieldType:StringField':

                self.fields.append(
                    ExtensionStringField(field_name,
                                       schemata="categorization",
                                       searchable=True,
                                       widget=StringWidget(
                                           label=facet.display_title,
                                           description=facet.description
                                       )))
            elif vocabularies == 'FieldType:KeywordField' or not vocabularies:
                self.fields.append(
                    ExtensionKeywordField(field_name,
                                          schemata="categorization",
                                          multiValued=1,
                                          accessor=field_name,
                                          searchable=True,
                                          widget=KeywordWidget(
                                              label=facet.display_title,
                                              description=facet.description))
                )
            else:
                self.fields.append(
                    ExtensionKeywordField(field_name,
                                          schemata="categorization",
                                          multiValued=1,
                                          accessor=field_name,
                                          searchable=True,
                                          widget=InAndOutWidget(
                                              label=facet.display_title,
                                              description=facet.description),
                                          vocabulary=vocabularies)
                )



        # build up our fields list from the registery settings
        #self.defaultRereviewDaysWait = settings.defaultRereviewDaysWait
        #self.defaultApplyToContent = settings.defaultApplyToContent

    def getOrder(self, schematas):
        """ Manipulate the order in which fields appear.

        @param schematas: Dictonary of schemata name -> field lists

        @return: Dictionary of reordered field lists per schemata.
        """
#        # insert 'revisitDate' right after 'effectiveDate'
#        order = schematas['dates']
#        if 'effectiveDate' in order and 'revisitDate' in order:
#            order.pop(order.index('revisitDate'))
#            order.insert(order.index('effectiveDate')+1, 'revisitDate')
#            schematas['dates'] = order
#
        return schematas

    def getFields(self):
        """@return: List of new fields we contribute to content."""
        return self.fields
