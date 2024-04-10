#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.generations.evolve1 module

This module is updating thesaurus extracts internal terms structure.
"""

__docformat__ = 'restructuredtext'

from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts
from pyams_utils.registry import get_local_registry, get_utilities_for, set_local_registry


def evolve(site):
    """Evolve 1: update thesaurus extracts terms"""
    old_registry = get_local_registry()
    try:
        registry = site.getSiteManager()
        set_local_registry(registry)
        # Update thesaurus extracts
        for name, thesaurus in get_utilities_for(IThesaurus):
            extracts = IThesaurusExtracts(thesaurus, None)
            if (extracts is not None) and (len(extracts) > 0):
                print(f"Updating terms for thesaurus « {name} »")
                for term in thesaurus.terms.values():
                    for extract_name in (term.extracts or ()):
                        extract = extracts.get(extract_name)
                        if extract is not None:
                            terms = extract.terms or set()
                            terms.add(term)
                            extract.terms = terms
    finally:
        set_local_registry(old_registry)
