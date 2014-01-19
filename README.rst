.. contents::

.. image:: https://secure.travis-ci.org/collective/collective.facets.png
    :target: http://travis-ci.org/collective/collective.facets


Introduction
============

Provide a control panel for site administrators to add additional facets to classify their content.
Facets are keyword fields added to the categorisation tab of all content types across your site.
If you are looking for fields just on certain content types then look instead at
Dexterity_ or `archetypes.schemaextender`_.

All fields are available to be used
in criteria for collections and viewable in the tabular view of a collection. They are easy to
use with plugins such as `eea.facetednavigation`_, `collective.portlet.filtersearch`_ or
`collective.portlet.collectionbysubject`_.
These field values aren't viewable on the item itself and aren't included in the html head metadata fields. They are
designed to aid in internal organisation of content only.

This plugin is similar to `collective.pigeonhole`_. c.pegeonhole allows for more
field types by using the schemaeditor, how it doesn't yet work with indexes and
collections.


Functionality
=============
A site administrator can:

 - Add a new facet
 - Remove a facet
 - Edit the description and title which will appear on /edit and also on collections
 - Specify a vocabulary which the field has to use

Compatibility
=============
Currently only works with in Plone 4.2 with new style collections and Archetypes.

Future Functionality
====================

 - Rename a facet without losing values (#TODO)
 - Make a facet required (#TODO)
 - Make a facet have an enforced vocabulary, perhaps via ATVocabularyManager (#TODO)
 - Rename values (#TODO)
 - Hide the default "Keywords" field (#TODO)
 - Support for dexterity


.. _Dexterity: http://plone.org/products/dexterity
.. _archetypes.schemaextender: http://pypi.python.org/pypi/archetypes.schemaextender
.. _eea.facetednavigation: http://plone.org/products/eea.facetednavigation
.. _collective.portlet.filtersearch: http://pypi.python.org/pypi/collective.portlet.filtersearch
.. _collective.portlet.collectionbysubject: http://pypi.python.org/pypi/collective.portlet.collectionbysubject
.. _collective.pigeonhole: https://github.com/davisagli/collective.pigeonhole