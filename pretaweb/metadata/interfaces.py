"""

    Define interfaces for your add-on.

"""

import zope.interface
from zope import schema


class IAddOnInstalled(zope.interface.Interface):
    """A layer specific for this add-on product.

    This interface is referred in browserlayers.xml.

    All views and viewlets register against this layer will appear on your Plone site
    only when the add-on installer has been run.
    """



def contentTypesVocabulary ():
    return schema.vocabulary.SimpleVocabulary.fromValues(["apples", "oranges", "pares"])


class IMetadataSettings (zope.interface.Interface):

    metadata = schema.Set(
            title=(u"Additional Metadata Fields"),
            description=(u"Names of additional keyword fields"),
            default=set([]),
            required=False,
            value_type=schema.TextLine(title=u"Field Name"))


