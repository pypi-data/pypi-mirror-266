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

"""PyAMS_thesaurus.api.rest module

Thesaurus REST API module.
"""

import sys

from colander import MappingSchema, SchemaNode, SequenceSchema, String, drop
from cornice import Service
from cornice.validators import colander_validator
from hypatia.text import ParseError
from pyramid.httpexceptions import HTTPBadRequest, HTTPOk

from pyams_security.interfaces.base import USE_INTERNAL_API_PERMISSION
from pyams_security.rest import check_cors_origin, set_cors_headers
from pyams_thesaurus.interfaces import REST_EXTRACTS_GETTER_ROUTE, REST_TERMS_SEARCH_ROUTE
from pyams_thesaurus.interfaces.term import STATUS_ARCHIVED
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts
from pyams_utils.interfaces.form import NO_VALUE_STRING
from pyams_utils.list import unique
from pyams_utils.registry import query_utility
from pyams_utils.rest import BaseResponseSchema, BaseStatusSchema, STATUS, http_error, rest_responses

__docformat__ = 'restructuredtext'


TEST_MODE = sys.argv[-1].endswith('/test')


#
# Thesaurus extracts getter services
#

class ThesaurusExtractsQuery(MappingSchema):
    """Thesaurus extracts getter schema"""
    thesaurus_name = SchemaNode(String(),
                                description="Selected thesaurus name")


class ThesaurusExtract(MappingSchema):
    """Thesaurus extracts getter result schema"""
    id = SchemaNode(String(),
                    description="Extract ID")
    text = SchemaNode(String(),
                      description="Extract name")


class ThesaurusExtractsList(SequenceSchema):
    """Thesaurus extracts result schema"""
    extract = ThesaurusExtract()


class ThesaurusExtractsSearchResults(BaseStatusSchema):
    """Thesaurus extracts results schema"""
    results = ThesaurusExtractsList(description="Thesaurus extracts list",
                                    missing=drop)


extracts_service = Service(name=REST_EXTRACTS_GETTER_ROUTE,
                           pyramid_route=REST_EXTRACTS_GETTER_ROUTE,
                           description="Thesaurus extracts management")


@extracts_service.options(validators=(check_cors_origin, set_cors_headers))
def extracts_options(request):  # pylint: disable=unused-argument
    """Extracts service OPTIONS handler"""
    return ''


class ThesaurusExtractsRequest(MappingSchema):
    """Thesaurus extracts request"""
    querystring = ThesaurusExtractsQuery()


class ThesaurusExtractsResponse(MappingSchema):
    """Thesaurus extracts getter response"""
    body = ThesaurusExtractsSearchResults()


extracts_get_responses = rest_responses.copy()
extracts_get_responses[HTTPOk.code] = ThesaurusExtractsResponse(
    description="Thesaurus extracts query response")


@extracts_service.get(permission=USE_INTERNAL_API_PERMISSION,
                      schema=ThesaurusExtractsRequest(),
                      validators=(check_cors_origin, colander_validator, set_cors_headers),
                      response_schemas=extracts_get_responses)
def get_extracts(request):
    """Get thesaurus extracts list"""
    params = request.params if TEST_MODE else request.validated.get('querystring', {})
    thesaurus_name = params.get('thesaurus_name')
    if not thesaurus_name:
        return http_error(request, HTTPBadRequest, 'missing argument')
    if thesaurus_name == NO_VALUE_STRING:
        return {
            'status': STATUS.SUCCESS.value,
            'results': []
        }
    thesaurus = query_utility(IThesaurus, name=thesaurus_name)
    if thesaurus is None:
        return http_error(request, HTTPBadRequest, 'bad thesaurus name')
    extracts = IThesaurusExtracts(thesaurus)
    return {
        'status': STATUS.SUCCESS.value,
        'results': [
            {
                'id': extract.name,
                'text': extract.name
            }
            for extract in extracts.values()
        ]
    }


#
# Thesaurus terms search services
#

class ThesaurusTermsQuery(MappingSchema):
    """Thesaurus terms search schema"""
    thesaurus_name = SchemaNode(String(),
                                description="Selected thesaurus name")
    extract_name = SchemaNode(String(),
                              description="Selected extract name",
                              missing=drop)
    term = SchemaNode(String(),
                      description="Terms search string")


class ThesaurusTerm(MappingSchema):
    """Thesaurus term"""
    id = SchemaNode(String(),
                    description="Term ID")
    text = SchemaNode(String(),
                      description="Term label")


class ThesaurusTermsList(SequenceSchema):
    """Thesaurus search results interface"""
    term = ThesaurusTerm()


class ThesaurusTermsSearchResults(BaseResponseSchema):
    """Thesaurus search results schema"""
    results = ThesaurusTermsList(description="Results list",
                                 missing=drop)


terms_service = Service(name=REST_TERMS_SEARCH_ROUTE,
                        pyramid_route=REST_TERMS_SEARCH_ROUTE,
                        description="Thesaurus terms management")


@terms_service.options(validators=(check_cors_origin, set_cors_headers))
def terms_options(request):  # pylint: disable=unused-argument
    """Terms service OPTIONS handler"""
    return ''


class ThesaurusTermsRequest(MappingSchema):
    """Terms getter request"""
    querystring = ThesaurusTermsQuery()


class ThesaurusTermsResponse(MappingSchema):
    """Terms getter response"""
    body = ThesaurusTermsSearchResults()


terms_get_responses = rest_responses.copy()
terms_get_responses[HTTPOk.code] = ThesaurusTermsResponse(
    description="List of terms matching given query")


@terms_service.get(permission=USE_INTERNAL_API_PERMISSION,
                   schema=ThesaurusTermsRequest(),
                   validators=(check_cors_origin, colander_validator, set_cors_headers),
                   response_schemas=terms_get_responses)
def get_terms(request):
    """Returns list of terms matching given query"""
    params = request.params if TEST_MODE else request.validated.get('querystring', {})
    thesaurus_name = params.get('thesaurus_name')
    extract_name = params.get('extract_name')
    query = params.get('term')
    if not (thesaurus_name or query):
        return {
            'status': STATUS.ERROR.value,
            'message': "Missing arguments"
        }
    thesaurus = query_utility(IThesaurus, name=thesaurus_name)
    if thesaurus is None:
        return {
            'status': STATUS.ERROR.value,
            'message': "Thesaurus not found"
        }
    try:
        return {
            'status': STATUS.SUCCESS.value,
            'results': [
                {
                    'id': term.label,
                    'text': term.label
                }
                for term in unique(thesaurus.find_terms(query, extract_name,
                                                        exact=True, stemmed=True))
                if term.status != STATUS_ARCHIVED
            ]
        }
    except ParseError:
        return {}
