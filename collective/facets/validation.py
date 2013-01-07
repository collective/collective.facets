import re
from collective.facets import facetsMessageFactory as _
from zope.schema import ValidationError


class InvalidId(ValidationError):
    __doc__ = _("""Id must only contains alphanumeric or underscore,
        starting with alpha.""")


def validate_id(value):
    """
    Check that id only contains alphanumeric or underscore,
    starting with alpha.
    """
    # http://plone.org/documentation/manual/developer-manual/forms/
    # using-zope.formlib/adding-validation
    if not re.match("^[A-Za-z][A-Za-z0-9_]*$", value):
        raise InvalidId(value)
    return True
