"""

    Retrofit re-review dates to Archetypes schema.

"""


from zope.component import adapts, getUtility
from zope.interface import implements

from Products.Archetypes.public import BooleanWidget, KeywordWidget
from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes import public as atapi
from Products.Archetypes.interfaces import IBaseContent

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender, IOrderableSchemaExtender, IBrowserLayerAwareExtender

from plone.registry.interfaces import IRegistry

from pretaweb.metadata.interfaces import IAddOnInstalled, IMetadataSettings


from datetime import datetime, timedelta

class ExtensionKeywordField(ExtensionField, atapi.LinesField):
    """ Retrofitted keyword field """


class MetadataDefault(object):

    def __init__ (self, context):
        self.context = context
        registry = getUtility(IRegistry)
        settings = registry.forInterface (IRereviewSettings)

        self.defaultRereviewDaysWait = settings.defaultRereviewDaysWait
        self.defaultApplyToContent = settings.defaultApplyToContent
        

    def __call__ (self):

        if self.defaultApplyToContent:
            tInfo = self.context.getTypeInfo()
            if tInfo.getId() in self.defaultApplyToContent:
                reReviewDate = datetime.now() + timedelta(days=self.defaultRereviewDaysWait)
                return reReviewDate.date().isoformat()
        return None



    

class MetadataExtender(object):
    """
    Add a series of "facets" or categorisation fields to a type
    """
    
    # This extender will apply to all Archetypes based content 
    adapts(IBaseContent)
    
    # We use both orderable and browser layer aware sensitive properties
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    
    # Don't do schema extending unless our add-on product is installed on Plone site
    layer = IAddOnInstalled


    def __init__(self, context):
        self.context = context

        registry = getUtility(IRegistry)
        settings = registry.forInterface (IMetadataSettings)

        #fake it for now
        # for facet in settings.facetList
        self.fields = []
        for field_name in settings.metadata:
            self.fields.append(
                ExtensionKeywordField(field_name,
                    schemata="categorization",
                    multiValued=1,
                    accessor=field_name,
                    searchable=True,
                    widget=KeywordWidget(
                        label=field_name,
                        description=u'%s Tags'%field_name,
                        ),
                )
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
        """
        @return: List of new fields we contribute to content. 
        """
        return self.fields
    
