"""

    Define interfaces for your add-on.

"""

from zope.interface import Interface


from zope import schema
from schema import implements
from plone.registry.field import PersistentField
from collective.facets import facetsMessageFactory as _


class IAddOnInstalled(Interface):
    """A layer specific for this add-on product.

    This interface is referred in browserlayers.xml.

    All views and viewlets register against this layer will appear on your Plone site
    only when the add-on installer has been run.
    """

class PersistentObject(PersistentField, schema.Object):
    pass


def contentTypesVocabulary ():
    return schema.vocabulary.SimpleVocabulary.fromValues(["apples", "oranges", "pares"])

class IFacetDefinition(Interface):
    name = schema.ASCIILine(title=_(u"Facet Name"), required=True)
    description = schema.ASCIILine(title=_(u"Description"), required=False)

class IFacetSettings (Interface):
    pass


# only used for the control panel dialog.
class IFacetEditSettings (Interface):

    facets = schema.Tuple(
            title=_(u'Additional Facet Fields'),
            description=(u"Names of additional keyword fields"),
            value_type=PersistentObject(IFacetDefinition, title=_(u"Facet Definition")),
            required=False,
            default=(),
            missing_value=(),
    )


from z3c.form.object import registerFactoryAdapter

class FacetDefinition(object):
    implements(IFacetDefinition)


registerFactoryAdapter(IFacetDefinition, FacetDefinition)
