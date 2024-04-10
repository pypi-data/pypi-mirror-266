=======================
PyAMS thesaurus package
=======================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pprint import pprint, pformat
    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)
    >>> from pyams_zmi import includeme as include_zmi
    >>> include_zmi(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_thesaurus import includeme as include_thesaurus
    >>> include_thesaurus(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...
    Upgrading PyAMS security to generation 2...
    Upgrading PyAMS thesaurus to generation 2...

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))

NLTK library must first be initialized before using text indexes:

    >>> import nltk
    >>> from pyams_utils.context import capture_all
    >>> with capture_all(nltk.download, 'punkt') as (status1, log1, errors1):
    ...     pass
    >>> status1
    True
    >>> with capture_all(nltk.download, 'snowball_data') as (status2, log2, errors2):
    ...     pass
    >>> status2
    True
    >>> with capture_all(nltk.download, 'stopwords') as (status3, log3, errors3):
    ...     pass
    >>> status3
    True


Creating a thesaurus from a SKOS RDF file
-----------------------------------------

A thesaurus is a persistent object stored in the Zope Object DataBase and recorded as a named
utility; a thesaurus is also a btree-based container which will contain terms and handle it's
own "private" catalog.

The quickest way to fill a thesaurus is done by importing contents of an XML file containing
thesaurus terms; several formats are available, the most common being SKOS/RDF:

    >>> import os
    >>> from pyams_thesaurus.tests.test_utilsdocs import CURRENT_DIR
    >>> from pyams_thesaurus.loader.skos import SKOSThesaurusLoader

    >>> datafile = os.path.join(CURRENT_DIR, '..', 'doctests', 'data', 'SAMPLE-SKOS.xml')
    >>> with open(datafile) as data:
    ...     loader = SKOSThesaurusLoader()
    ...     thesaurus = loader.load(data)

When the thesaurus is loaded, we can get access to it's description and terms:

    >>> thesaurus.title
    "Th\xe9saurus Naturaliste de l'Office National des For\xeats"
    >>> thesaurus.description
    " Th\xe9saurus des r\xe9seaux naturalistes de l'Office National des For\xeats. "
    >>> thesaurus.created
    datetime.date(2011, 6, 1)

    >>> thesaurus.language
    'fr'
    >>> len(thesaurus.terms)
    2981

Top terms are those which are at the first level of the hierarchy and don't have any generic
term and which are parented to themselves:

    >>> len(thesaurus.top_terms)
    9

    >>> sorted([term.label for term in thesaurus.top_terms])
    ['Ecologie des esp\xe8ces', 'Environnement', 'Habitat', 'Index g\xe9ographique', 'Intervention humaine',
    'Mots-outils', 'M\xe9thodologie naturaliste', "Protection de l'environnement", "Science de l'environnement"]

    >>> thesaurus.terms.get('Environnement').generic is None
    True

    >>> thesaurus.terms.get('Environnement').parent.label
    'Environnement'

    >>> thesaurus.terms.get('Intensification').parent.label
    'Intervention humaine'

    >>> sorted([term.label for term in thesaurus.terms.get('Intensification').specifics])
    []

So a given term can be linked directly to only one generic and zero or more specific terms, to create a hierarchy:

    >>> thesaurus.terms.get('Intensification').generic.label
    'Surexploitation de la nature'

    >>> sorted([term.label for term in thesaurus.terms.get('Surexploitation de la nature').specifics])
    ['Agriculture intensive', 'D\xe9forestation', 'D\xe9gradation du sol', 'D\xe9sertification',
    'Intensification', 'Surp\xeache']

It's then possible to get a term's parents ; result is ordered, from first to last parent:

    >>> [term.label for term in thesaurus.terms.get('Surexploitation de la nature').get_parents()]
    ['Impact des activit\xe9s humaines', 'Intervention humaine']

The "level" of a term is his depth in the hierarchy
    >>> thesaurus.terms.get('Surexploitation de la nature').level
    3

To get "brothers" of a term:

    >>> sorted([term.label for term in thesaurus.terms.get('Surexploitation de la nature').get_siblings()])
    ['Anthropisation', 'S\xe9quelle de guerre']

And to get the full sub-hierarchy of a given term:

    >>> sorted([term.label for term in thesaurus.terms.get('Surexploitation de la nature').get_all_children()])
    ['Agriculture intensive', 'D\xe9boisement', 'D\xe9forestation', 'D\xe9frichement',
    'D\xe9gradation du sol', 'D\xe9sertification', 'Epuisement du sol', 'Erosion',
    'Intensification', 'Surpat\xfbrage', 'Surp\xeache', 'Tassement du sol']

A term can also be associated to several terms, outside it's hierarchy or not:

    >>> sorted([term.label for term in thesaurus.terms.get('D\xe9forestation').associations])
    ['Destruction de l\u2019habitat', 'D\xe9gradation des for\xeats', 'Exploitation foresti\xe8re',
    'For\xeat', "R\xe9duction de l'habitat"]


Creating a thesaurus from a SuperDoc export thesaurus file
----------------------------------------------------------

SuperDoc is a custom application used to handle bibliographic references, which handles thesauri
and have a custom export format in XML.

The Superdoc loader uses the same interface, but a configuration is required to define thesaurus
language. You can also notice that the thesaurus loading method is quite different here from the
previous one used for SKOS as the thesaurus is created before loading XML content into it, while
it was created by the loader in the previous example; but both methods can be used for all
loaders:

    >>> from pyams_thesaurus.thesaurus import Thesaurus
    >>> from pyams_thesaurus.loader.config import ThesaurusLoaderConfiguration

    >>> thesaurus = Thesaurus()

    >>> config = ThesaurusLoaderConfiguration()
    >>> config.language = 'fr'
    >>> config.format = 'SuperDoc'

    >>> datafile = os.path.join(CURRENT_DIR, '..', 'doctests', 'data', 'SAMPLE-Superdoc.xml')
    >>> with open(datafile) as data:
    ...     config.data = ('sample.xml', data)
    ...     thesaurus.load(config)

    >>> thesaurus.language
    'en'
    >>> len(thesaurus.terms)
    2472

Top terms are those which are at the first level of the hierarchy and don't have any generic
term and which are parented to themselves:

    >>> len(thesaurus.top_terms)
    465

    >>> sorted([term.label for term in thesaurus.top_terms])
    ['Abri', 'Accident du travail', 'Accueil du public', 'Acidification du sol', ..., 'pH', 'test']

    >>> sorted([term.label for term in thesaurus.get_top_terms()])
    ['Abri', 'Accident du travail', 'Accueil du public', 'Acidification du sol', ..., 'pH', 'test']

    >>> thesaurus.terms.get('Abri').generic is None
    True

    >>> thesaurus.terms.get('Abri').parent.label
    'Abri'

    >>> thesaurus.terms.get('Eclaircie').parent.label
    'Sylviculture'

    >>> sorted([term.label for term in thesaurus.terms.get('Couvert').specifics])
    []

Nodes are used to display thesaurus terms tree:

    >>> term = thesaurus.terms.get('Abri')
    >>> nodes = []
    >>> thesaurus.get_nodes(term, nodes)
    >>> pprint(nodes)
    [{'css_class': 'published',
      'expand': False,
      'extensions': [{'active': False,
                      'icon': 'fas fa-font',
                      'name': 'html',
                      'title': 'Rich text description',
                      'view': 'http://localhost/++terms++/Abri%20lat%C3%A9ral/html-description.html'}],
      'extracts': [],
      'label': 'Abri latéral',
      'view': 'http://localhost/++terms++/Abri%20lat%C3%A9ral/properties.html'},
     {'css_class': 'published',
      'expand': False,
      'extensions': [{'active': False,
                      'icon': 'fas fa-font',
                      'name': 'html',
                      'title': 'Rich text description',
                      'view': 'http://localhost/++terms++/Abri%20vertical/html-description.html'}],
      'extracts': [],
      'label': 'Abri vertical',
      'view': 'http://localhost/++terms++/Abri%20vertical/properties.html'}]


Searching terms requires a catalog:

    >>> from pyams_utils.list import unique

    >>> app['thesaurus'] = thesaurus
    >>> thesaurus.init_catalog()

    >>> sorted(unique([term.label for term in thesaurus.find_terms('Abri', exact=True, exact_only=True)]))
    ['Abri']

    >>> sorted(unique([term.label for term in thesaurus.find_terms('Abri', exact=True, stemmed=True)]))
    ['Abri', 'Abri latéral', 'Abri pour le public', 'Abri serre', 'Abri vertical', "Coupe d'abri", 'Plantation sous abri', 'Tube abri']


So a given term can be linked directly to only one generic and zero or more specific terms, to create a hierarchy:

    >>> thesaurus.terms.get('Eclaircie').generic.label
    'Soins aux jeunes peuplements'

    >>> sorted([term.label for term in thesaurus.terms.get('Soins aux jeunes peuplements').specifics])
    ['D\xe9gagement de plantation', 'D\xe9gagement de semis', 'D\xe9pressage', 'D\xe9tourage',
    'Eclaircie', 'Nettoiement']

It's then possible to get a term's parents; result is ordered, from first to last parent:

    >>> [term.label for term in thesaurus.terms.get('Eclaircie').get_parents()]
    ['Soins aux jeunes peuplements', 'Sylviculture']

The "level" of a term is his depth in the hierarchy
    >>> thesaurus.terms.get('Eclaircie').level
    3

To get "brothers" of a term:

    >>> sorted([term.label for term in thesaurus.terms.get('Soins aux jeunes peuplements').get_siblings()])
    ['Cloisonnement', 'Coupe', "D\xe9signation d'arbres objectif", 'Elagage', 'Emondage', 'Martelage',
    'Populiculture', 'Pr\xe9d\xe9signation', 'Pr\xe9paration de la station', 'Rec\xe9page',
    'R\xe9g\xe9n\xe9ration', "Sylviculture d'arbres", 'Sylviculture de rattrapage', 'Sylviculture douce',
    'Sylviculture dynamique', 'Sylviculture intensive', 'Sylviculture traditionnelle', 'Taille de formation']

To get all children of a term's generic:

    >>> sorted([term.label for term in thesaurus.terms.get('Soins aux jeunes peuplements').generic.specifics])
    ['Cloisonnement', 'Coupe', "D\xe9signation d'arbres objectif", 'Elagage', 'Emondage', 'Martelage',
    'Populiculture', 'Pr\xe9d\xe9signation', 'Pr\xe9paration de la station', 'Rec\xe9page',
    'R\xe9g\xe9n\xe9ration', 'Soins aux jeunes peuplements', "Sylviculture d'arbres", 'Sylviculture de rattrapage',
    'Sylviculture douce', 'Sylviculture dynamique', 'Sylviculture intensive', 'Sylviculture traditionnelle',
    'Taille de formation']

And to get the full sub-hierarchy of a given term:

    >>> sorted([term.label for term in thesaurus.terms.get('Soins aux jeunes peuplements').get_all_children()])
    ['D\xe9gagement de plantation', 'D\xe9gagement de semis', 'D\xe9pressage', 'D\xe9pressage avec cloisonnement',
    'D\xe9pressage syst\xe9matique', 'D\xe9tourage', 'Eclaircie', 'Eclaircie par le bas', 'Eclaircie par le haut',
    'Eclaircie pr\xe9coce', 'Eclaircie sanitaire', 'Eclaircie syst\xe9matique', 'Eclaircie syst\xe9matique en ligne',
    'Eclaircie s\xe9lective', 'Eclaircie s\xe9lective avec cloisonnement', 'Eclaircie tardive',
    'Mise \xe0 distance', 'Nettoiement', 'Premi\xe8re \xe9claircie']

A term can also be linked to several synonyms; synonyms are stored outside of terms hierarchy.
Synonyms are always linked to an 'usage' term, which is the official term to use:

    >>> sorted([term.label for term in thesaurus.terms.get('Base de loisir').used_for])
    ['Base de plein air et de loisir']

Synonyms title includes label of their associated term:

    >>> sorted([term.title for term in thesaurus.terms.get('Base de loisir').used_for])
    ['Base de loisir [ Base de plein air et de loisir ]']

The reciprocity must be verified:

    >>> thesaurus.terms.get('Base de plein air et de loisir').usage.label
    'Base de loisir'

Finally, this kind of thesaurus can provide associations between words:

    >>> sorted([term.label for term in thesaurus.terms.get('Abri').associations])
    ["Coupe d'abri", 'Couvert', 'Plantation sous abri', 'Rayonnement solaire']


Using thesaurus terms extensions
--------------------------------

Extensions are small utilities that can be used to add additional information on any thesaurus
term. For example, an extension called *html* is provided by *PyAMS_thesaurus* package to
add an additional HTML text on any term:

    >>> term = thesaurus.terms.get('Abri')
    >>> term.extensions = {'html'}

When an extension is added to a term, the *target* marker interface of this extension is
added to the list of interfaces provided by the term:

    >>> from pyams_thesaurus.extension.html.interfaces import IThesaurusTermHTMLTarget
    >>> IThesaurusTermHTMLTarget.providedBy(term)
    True

You can then get access to the additional information provided by this extension:

    >>> from pyams_thesaurus.extension.html.interfaces import IThesaurusTermHTMLInfo
    >>> info = IThesaurusTermHTMLInfo(term)
    >>> info
    <pyams_thesaurus.extension.html.ThesaurusTermHTMLInfo object at 0x...>

    >>> term.extensions = ()
    >>> IThesaurusTermHTMLTarget.providedBy(term)
    False


Using thesaurus extracts
------------------------

A thesaurus can contain extracts, which are sub-sets of thesaurus terms. Each thesaurus term can
then be associated with zero or more extracts.

The main rule concerning the association between terms and extracts is that a term can be
associated with an extract only if it's generic term is also associated with it, and so
recursively.

    >>> term = thesaurus.terms.get('Soins aux jeunes peuplements')
    >>> sorted([t.label for t in term.generic.specifics])
    ['Cloisonnement', 'Coupe', "D\xe9signation d'arbres objectif", 'Elagage', 'Emondage', 'Martelage',
    'Populiculture', 'Pr\xe9d\xe9signation', 'Pr\xe9paration de la station', 'Rec\xe9page',
    'R\xe9g\xe9n\xe9ration', 'Soins aux jeunes peuplements', "Sylviculture d'arbres", 'Sylviculture de rattrapage',
    'Sylviculture douce', 'Sylviculture dynamique', 'Sylviculture intensive', 'Sylviculture traditionnelle',
    'Taille de formation']

    >>> term.extracts
    set()

    >>> from pyams_thesaurus.interfaces.thesaurus import IThesaurusExtracts
    >>> from pyams_thesaurus.thesaurus import ThesaurusExtract
    >>> extract = ThesaurusExtract()
    >>> extract.name = 'Thesaurus extract'
    >>> IThesaurusExtracts(thesaurus)[extract.name] = extract

If we try to set an extract on a term randomly, we won't always get the good result:

    >>> term.extracts = {extract.name}
    >>> term.extracts
    set()

Term extracts are still empty because term's generic is not associated to this extract.

    >>> term.generic.extracts = {extract.name}
    >>> term.add_extract(extract)
    >>> term.extracts
    {'Thesaurus extract'}

Of course, this works only because term's generic is a toplevel term; if not, we would have to define terms extracts
starting from the top terms hierarchy.

Resetting a term's extracts afterwards also reset extracts of it's specific terms:

    >>> term.generic.extracts = set()
    >>> term.extracts
    set()

Updating a term's extracts also updates it's synonyms extracts:

    >>> term = thesaurus.terms.get('Base de loisir')
    >>> term.extracts
    set()
    >>> [t.extracts for t in term.used_for]
    [set()]

An extract length is the length of it's terms set:

    >>> len(extract)
    0
    >>> extract.add_term(term, check=False)
    >>> len(extract)
    2
    >>> sorted(list(extract.terms_labels))
    ['Base de loisir', 'Base de plein air et de loisir']
    >>> len(list(extract.terms_ids))
    2

As you can see, term synonyms are also added to extract terms!

    >>> term.extracts
    {'Thesaurus extract'}

    >>> term in extract.terms
    True
    >>> term.label in extract.terms_labels
    True

    >>> nodes = []
    >>> extract.get_nodes(term, nodes)
    >>> pprint(nodes)
    []

    >>> [t.extracts for t in term.used_for]
    [{'Thesaurus extract'}]

    >>> extract.remove_term(term, check=False)
    >>> len(extract.terms)
    0
    >>> [t.extracts for t in term.used_for]
    [set()]


This sample thesaurus is a little buggy! Synonyms shouldn't have generic terms:

    >>> for t in list(reversed(term.get_parents()))+[term]:
    ...     t.extracts = {extract.name}
    >>> term.extracts
    {'Thesaurus extract'}
    >>> [t.extracts for t in term.used_for]
    [{'Thesaurus extract'}]

    >>> term.get_parents()[-1].extracts = set()
    >>> term.extracts
    set()
    >>> [t.extracts for t in term.used_for]
    [set()]


Merging thesaurus
-----------------

Terms can be merged when a thesaurus loader is used to load terms from a new file into an
existing thesaurus:

    >>> from pyams_thesaurus.loader.config import ThesaurusUpdaterConfiguration
    >>> config = ThesaurusUpdaterConfiguration()
    >>> config.format = 'SKOS (RDF)'
    >>> config.conflict_suffix = '(conflict)'

    >>> datafile = os.path.join(CURRENT_DIR, '..', 'doctests', 'data', 'SAMPLE-SKOS.xml')
    >>> with open(datafile) as data:
    ...     config.data = ('sample.xml', data)
    ...     thesaurus.merge(config)

    >>> len(thesaurus.terms)
    5050

    >>> len(thesaurus.top_terms)
    352


Exporting thesaurus
-------------------

You can also export thesaurus content into several formats; exporters are named utilities
providing IThesaurusExporter interface:

    >>> from pyams_utils.registry import get_utility
    >>> from pyams_thesaurus.interfaces.loader import IThesaurusExporter
    >>> from pyams_thesaurus.loader.config import ThesaurusExporterConfiguration

    >>> config = ThesaurusExporterConfiguration()
    >>> config.format = 'SKOS (RDF)'
    >>> exporter = get_utility(IThesaurusExporter, name=config.format)
    >>> output = exporter.export(thesaurus, config)
    >>> output
    <_io.BufferedRandom name=...>
    >>> pos = output.seek(0)
    >>> result = output.read()
    >>> output.close()
    >>> result[0:128]
    b'<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:r'

    >>> config = ThesaurusExporterConfiguration()
    >>> config.format = 'SuperDoc'
    >>> exporter = get_utility(IThesaurusExporter, name=config.format)
    >>> output = exporter.export(thesaurus, config)
    >>> output
    <_io.BufferedRandom name=...>
    >>> pos = output.seek(0)
    >>> result = output.read()
    >>> output.close()
    >>> result[0:128]
    b'<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n<Results xmlns="http://www.inmagic.com/webpublisher/query" productTitle='


Removing terms from thesaurus
-----------------------------

You can always remove a term from a thesaurus, but only if he doesn't have any specific term
and if it is not used as index key into a catalog:

    >>> term = thesaurus.terms.get('Base de loisir')
    >>> term.is_deletable()
    False

    >>> thesaurus.remove_term(term)
    Traceback (most recent call last):
    ...
    pyams_thesaurus.interfaces.ThesaurusTermDeleteException: Term can't be deleted

    >>> 'Effet direct' in thesaurus.terms
    True
    >>> term = thesaurus.terms.get('Effet direct')
    >>> term.is_deletable()
    True
    >>> thesaurus.remove_term(term)
    >>> 'Effet direct' in thesaurus.terms
    False


Tests cleanup:

    >>> tearDown()
