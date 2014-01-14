""" Portal tools specific vocabularies
"""
import operator
from zope.component import getUtilitiesFor
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
try:
    from zope.app.component.hooks import getSite
except:
    from zope.component.hooks import getSite
#from z3c.form.interfaces import NO_VALUE

try:
    # Don't blame me, blame #pyflakes
    from zope.schema import interfaces
    IVocabularyFactory = interfaces.IVocabularyFactory
except ImportError:
    # < Zope 2.10
    from zope.app.schema import vocabulary
    IVocabularyFactory = vocabulary.IVocabularyFactory

# from eea.faceted.vocabularies.utils import compare
def compare(a, b):
    """ Compare lower values """
    if not isinstance(a, unicode):
        a = a.decode('utf-8')
    if not isinstance(b, unicode):
        b = b.decode('utf-8')
    return cmp(a.lower(), b.lower())


#
# portal_vocabularies
#
class PortalVocabulariesVocabulary(object):
    """ Return vocabularies in portal_vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ See IVocabularyFactory interface
        """
        res = []
        # context always None, NO_VALUE or dict type
        #if not context or context == NO_VALUE or type(context) == dict:
        site_context = getSite()
        vtool = getToolByName(site_context, 'portal_vocabularies', None)
        if vtool:
            vocabularies = vtool.objectValues()
            res.extend([(term.getId(), term.title_or_id())
                        for term in vocabularies])
        atvocabulary_ids = [elem[0] for elem in res]

        factories = getUtilitiesFor(IVocabularyFactory)
        res.extend([(factory[0], factory[0]) for factory in factories
                    if factory[0] not in atvocabulary_ids])

        res.sort(key=operator.itemgetter(1), cmp=compare)
        res.insert(0, ('FieldType:KeywordField', 'Tags'))
        res.insert(0, ('FieldType:StringField', 'Free Text'))
        items = [SimpleTerm(key, key, value) for key, value in res]
        return SimpleVocabulary(items)

PortalVocabulariesVocabularyFactory = PortalVocabulariesVocabulary()
