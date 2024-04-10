#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.generations main module

This module provides site generation utility to automatically create
a thesaurus container on upgrade.
"""

import sys
from importlib import import_module

from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_thesaurus.interfaces.thesaurus import IThesaurusManager, THESAURUS_MANAGER_NAME
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


REQUIRED_UTILITIES = ((IThesaurusManager, '', None, THESAURUS_MANAGER_NAME),)


@utility_config(name='PyAMS thesaurus', provides=ISiteGenerations)
class ThesaurusGenerationsChecker:
    """Thesaurus generations checker"""

    order = 100
    generation = 2

    def evolve(self, site, current=None):  # pylint: disable=unused-argument,no-self-use
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)
        if not current:
            current = 1
        for generation in range(current, self.generation):
            module_name = f'pyams_thesaurus.generations.evolve{generation}'
            module = sys.modules.get(module_name)
            if module is None:
                module = import_module(module_name)
            module.evolve(site)
