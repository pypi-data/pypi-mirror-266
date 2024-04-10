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

"""PyAMS_*** module

"""

__docformat__ = 'restructuredtext'

import logging
from importlib import import_module

from zope.dublincore.interfaces import IZopeDublinCore

from pyams_catalog.generations import check_required_indexes
from pyams_catalog.i18n import I18nTextIndexWithInterface
from pyams_catalog.index import DatetimeIndexWithInterface, FieldIndexWithInterface, \
    KeywordIndexWithInterface
from pyams_catalog.interfaces import DATE_RESOLUTION, MINUTE_RESOLUTION
from pyams_catalog.nltk import get_fulltext_lexicon
from pyams_content.component.thesaurus import ICollectionsInfo, ITagsInfo, IThemesInfo
from pyams_content.interfaces import CONTRIBUTOR_ROLE, IBaseContent, IObjectTypes, MANAGER_ROLE, OWNER_ROLE, \
    PILOT_ROLE, WEBMASTER_ROLE
from pyams_content.reference.pictogram import IPictogramTable
from pyams_content.root import ISiteRootToolsConfiguration
from pyams_content.shared.alert.interfaces import IAlertManager
from pyams_content.shared.common.interfaces import IWfSharedContent
from pyams_content.shared.common.interfaces.types import IWfTypedSharedContent
from pyams_content.shared.form.interfaces import IFormManager
from pyams_content.shared.topic.interfaces import ITopicManager
from pyams_content.shared.view.interfaces import IViewManager
from pyams_security.index import PrincipalsRoleIndex
from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_thesaurus.index import ThesaurusTermsListFieldIndex
from pyams_utils.interfaces.traversing import IPathElements
from pyams_utils.registry import get_pyramid_registry, utility_config
from pyams_workflow.interfaces import IWorkflowPublicationInfo, IWorkflowState


LOGGER = logging.getLogger('PyAMS (content)')

REQUIRED_UTILITIES = ()

REQUIRED_TABLES = (
    (IPictogramTable, 'pictograms'),
)

REQUIRED_TOOLS = (
    (IViewManager, 'views'),
    (IAlertManager, 'alerts'),
    (IFormManager, 'forms'),
    (ITopicManager, 'topics')
)

REQUIRED_INDEXES = [
    ('object_types', KeywordIndexWithInterface, {
        'interface': IObjectTypes,
        'discriminator': 'object_types'
    }),
    ('content_type', FieldIndexWithInterface, {
        'interface': IBaseContent,
        'discriminator': 'content_type'
    }),
    ('data_type', FieldIndexWithInterface, {
        'interface': IWfTypedSharedContent,
        'discriminator': 'data_type'
    }),
    ('role:owner', PrincipalsRoleIndex, {
        'role_id': OWNER_ROLE
    }),
    ('role:pilot', PrincipalsRoleIndex, {
        'role_id': PILOT_ROLE
    }),
    ('role:manager', PrincipalsRoleIndex, {
        'role_id': MANAGER_ROLE
    }),
    ('role:contributor', PrincipalsRoleIndex, {
        'role_id': CONTRIBUTOR_ROLE
    }),
    ('role:webmaster', PrincipalsRoleIndex, {
        'role_id': WEBMASTER_ROLE
    }),
    ('parents', KeywordIndexWithInterface, {
        'interface': IPathElements,
        'discriminator': 'parents'
    }),
    ('workflow_state', FieldIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'state'
    }),
    ('workflow_principal', FieldIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'state_principal'
    }),
    ('modifiers', KeywordIndexWithInterface, {
        'interface': IWfSharedContent,
        'discriminator': 'modifiers'
    }),
    ('created_date', DatetimeIndexWithInterface, {
        'interface': IZopeDublinCore,
        'discriminator': 'created',
        'resolution': DATE_RESOLUTION
    }),
    ('modified_date', DatetimeIndexWithInterface, {
        'interface': IZopeDublinCore,
        'discriminator': 'modified',
        'resolution': DATE_RESOLUTION
    }),
    ('publication_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'publication_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('effective_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'publication_effective_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('push_end_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'push_end_date_index',
        'resolution': MINUTE_RESOLUTION
    }),
    ('expiration_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'publication_expiration_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('first_publication_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'first_publication_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('content_publication_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'content_publication_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('visible_publication_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowPublicationInfo,
        'discriminator': 'visible_publication_date',
        'resolution': MINUTE_RESOLUTION
    }),
    ('tags', ThesaurusTermsListFieldIndex, {
        'interface': ITagsInfo,
        'discriminator': 'tags',
        'include_parents': False,
        'include_synonyms': False
    }),
    ('themes', ThesaurusTermsListFieldIndex, {
        'interface': IThemesInfo,
        'discriminator': 'themes',
        'include_parents': False,
        'include_synonyms': False
    }),
    ('themes_tree', ThesaurusTermsListFieldIndex, {
        'interface': IThemesInfo,
        'discriminator': 'themes',
        'include_parents': True,
        'include_synonyms': False
    }),
    ('themes_all', ThesaurusTermsListFieldIndex, {
        'interface': IThemesInfo,
        'discriminator': 'themes',
        'include_parents': True,
        'include_synonyms': True
    }),
    ('collections', ThesaurusTermsListFieldIndex, {
        'interface': ICollectionsInfo,
        'discriminator': 'collections',
        'include_parents': False,
        'include_synonyms': False
    })
]


#
# Checker for required shared tables
#

def check_required_tables(site, tables=REQUIRED_TABLES, registry=None):
    """Check for required reference tables

    :param site: site root to check for tables
    :param tables: iterable of reference tables to check or create; each occurrence is a tuple
        of three elements containing configuration attribute name, default table name and table
        factory
    :param registry: optional registry object

    For each table which may be registered, the check if it's already defined into current site
    configuration; if not, a factory lookup is done: a custom factory can be defined using a
    setting named *pyams_content.config.{name}_factory*, where name is the default tool name;
    otherwise, a default object factory lookup for the given interface is made; when the factory
    is found, the tool is created and stored into site configuration.

    Custom table name can be provided into configuration file using a setting called
    *pyams_content.config.${table_name}_table_name*.
    """

    if registry is None:
        registry = get_pyramid_registry()
    configuration = ISiteRootToolsConfiguration(site)
    for interface, name in tables:
        configuration.check_table(interface, name, registry)


#
# Checker for required shared tools
#

def check_required_tools(site, tools=REQUIRED_TOOLS, registry=None):
    """Check for required shared tools

    :param site: site root to check for tools
    :param tools: iterable of shared tools to check or create; each occurrence is a tuple of
        two elements containing the tool interface and its default name.
    :param registry: optional registry object

    For each tool which may be registered, the check if it's already defined into current site
    configuration; if not, a factory lookup is done: a custom factory can be defined using a
    setting named *pyams_content.config.{name}_factory*, where name is the default tool name;
    otherwise, a default object factory lookup for the given interface is made; when the factory
    is found, the tool is created and stored into site configuration.

    Custom shared tool name can be provided into configuration file using a setting called
    *pyams_content.config.${table_name}_tool_name*.
    """

    if registry is None:
        registry = get_pyramid_registry()
    configuration = ISiteRootToolsConfiguration(site)
    for interface, name in tools:
        configuration.check_tool(interface, name, registry)


def get_required_indexes():
    """Get list of required indexes based on lexicon settings"""
    indexes = REQUIRED_INDEXES
    registry = get_pyramid_registry()
    for code, language in map(lambda x: x.split(':'),
                              registry.settings.get('pyams_content.lexicon.languages',
                                                    'en:english').split()):
        indexes.append(('title:{0}'.format(code), I18nTextIndexWithInterface, {
            'language': code,
            'interface': IBaseContent,
            'discriminator': 'title',
            'lexicon': lambda: get_fulltext_lexicon(language)
        }))
    return indexes


@utility_config(name='PyAMS content', provides=ISiteGenerations)
class WebsiteGenerationsChecker:
    """PyAMS content package generations checker"""

    order = 100
    generation = 1

    def evolve(self, site, current=None):
        """Check for required utilities, tables and tools"""
        check_required_utilities(site, REQUIRED_UTILITIES)
        check_required_indexes(site, get_required_indexes())
        check_required_tables(site, REQUIRED_TABLES)
        check_required_tools(site, REQUIRED_TOOLS)

        if not current:
            current = 1
        for generation in range(current, self.generation):
            module_name = 'pyams_content.generations.evolve{}'.format(generation)
            module = import_module(module_name)
            module.evolve(site)
