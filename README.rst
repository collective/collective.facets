.. contents::

.. image:: https://secure.travis-ci.org/collective/collective.facets.png
    :target: http://travis-ci.org/collective/collective.facets


Introduction
============

Provide a control panel for site administrators to add additional facets to classify their content.
Facets are keyword, text or fixed vocabulary fields added to the categorisation
tab of all content types across your site.
If you are looking for fields just on certain content types then look instead at
Dexterity_ or `archetypes.schemaextender`_.

All fields are available to be used
in criteria for collections and viewable in the tabular view of a collection. They are easy to
use with plugins such as `eea.facetednavigation`_, `collective.portlet.filtersearch`_ or
`collective.portlet.collectionbysubject`_.

These field values aren't viewable on the item itself and aren't included in the
html head metadata fields. They are
designed to aid in internal organisation of content only.
If you'd like the fields to appear in the view of the item you can use
`collective.listingviews`_ or use another method to create a new view template.


Related Plugins
===============

`collective.pigeonhole`_: c.pegeonhole allows for more
field types by using the schemaeditor, how it doesn't yet work with indexes and
collections.

`collective.taxonomysupport`_: creates a new field on content and criterian in
collections but also sets the vocabulary of the field to be determined by special
folders in the content area.

`redomino.advancedkeyword`_: changes the default tags field to be hierarchical.

`collective.taxonomy`_: Allows you to create and manage large heirachical
vocabularies (aka a taxonomy). Is applied to Dexterity content via by creating
behaviours and then applying those behaviours to the content types you want.
Works with collections.
Doesn't support other kinds of fields other than taxomony.

`collective.categorizing`_: TODO

`metanav`_: TODO


Functionality
=============
A site administrator can:

 - Add a new facet
 - Remove a facet
 - Edit the description and title which will appear on /edit and also on collections
 - Specify the facet as either a TextField, Keyword/Folksomony or selected from
   an enforced vocabulary.

Compatibility
=============
Works with Plone 4.1, 4.2 and 4.3. Works with both new style collections and old
style. Currently only works with Archetypes not Dexterity


Future Functionality
====================

 - Rename a facet without losing values (#TODO)
 - Make a facet required (#TODO)
 - Rename values (#TODO)
 - Hide the default "Keywords" field (#TODO)
 - Support for dexterity


.. _Dexterity: http://plone.org/products/dexterity
.. _archetypes.schemaextender: http://pypi.python.org/pypi/archetypes.schemaextender
.. _eea.facetednavigation: http://plone.org/products/eea.facetednavigation
.. _collective.portlet.filtersearch: http://pypi.python.org/pypi/collective.portlet.filtersearch
.. _collective.portlet.collectionbysubject: http://pypi.python.org/pypi/collective.portlet.collectionbysubject
.. _collective.pigeonhole: https://github.com/davisagli/collective.pigeonhole
.. _collective.listingviews: https://github.com/collective/collective.listingviews
.. _collective.taxonomysupport: http://plone.org/products/collective.taxonomysupport
.. _redomino.advancedkeyword: http://pypi.python.org/pypi/redomino.advancedkeyword
.. _collective.categorizing: http://plone.org/products/collective.categorizing
.. _metanav: http://plone.org/products/metanav
.. _collective.taxonomy: https://pypi.python.org/pypi/collective.taxonomy