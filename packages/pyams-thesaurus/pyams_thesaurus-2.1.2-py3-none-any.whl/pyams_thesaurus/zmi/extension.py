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

"""PyAMS_thesaurus.zmi.extension module

This module defines base components for extensions management.
"""

from pyams_thesaurus.interfaces import MANAGE_THESAURUS_CONTENT_PERMISSION
from pyams_thesaurus.interfaces.term import IThesaurusTerm
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_utils.adapter import adapter_config
from pyams_utils.traversing import get_parent
from pyams_zmi.form import AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'


class ThesaurusTermExtensionEditForm(AdminModalEditForm):
    """Thesaurus term extension properties edit form"""

    _edit_permission = MANAGE_THESAURUS_CONTENT_PERMISSION


@adapter_config(required=(IThesaurusTerm, IAdminLayer, ThesaurusTermExtensionEditForm),
                provides=IFormTitle)
def thesaurus_term_extension_form_title(context, request, form):
    """Thesaurus term extension form title"""
    thesaurus = get_parent(context, IThesaurus)
    return TITLE_SPAN_BREAK.format(
        get_object_label(thesaurus, request, form),
        get_object_label(context, request, form, name='form-title'))
