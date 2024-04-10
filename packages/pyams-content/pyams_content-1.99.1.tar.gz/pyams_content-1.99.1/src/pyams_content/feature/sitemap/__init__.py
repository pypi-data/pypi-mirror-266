#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content.feature.sitemap module

This module defines main sitemap management components.
"""

__docformat__ = 'restructuredtext'

from datetime import datetime
from itertools import product

from hypatia.catalog import CatalogQuery
from hypatia.interfaces import ICatalog
from hypatia.query import Any, Eq
from pyramid.view import view_config
from zope.intid import IIntIds
from zope.schema.vocabulary import getVocabularyRegistry

from pyams_catalog.query import CatalogResultSet
from pyams_content.feature.sitemap.interfaces import ISitemapExtension
from pyams_content.root import ISiteRootToolsConfiguration
from pyams_content.shared.common import IBaseSharedTool, SHARED_CONTENT_TYPES_VOCABULARY
from pyams_i18n.interfaces import II18nManager
from pyams_layer.interfaces import IPyAMSUserLayer
from pyams_site.interfaces import ISiteRoot
from pyams_utils.list import unique_iter
from pyams_utils.registry import get_all_utilities_registered_for, get_utility
from pyams_utils.timezone import tztime
from pyams_workflow.interfaces import IWorkflow, IWorkflowPublicationInfo


@view_config(name='robots.txt',
             context=ISiteRoot, request_type=IPyAMSUserLayer,
             renderer='templates/robots.pt')
def site_root_robots_view(request):
    """Site root robots.txt view"""
    request.response.content_type = 'text/plain'
    return {
        'tools_configuration': ISiteRootToolsConfiguration(request.root),
        'disallow': [
            tool
            for tool in get_all_utilities_registered_for(IBaseSharedTool)
            if not tool.shared_content_menu
        ]
    }


@view_config(name='humans.txt',
             context=ISiteRoot, request_type=IPyAMSUserLayer,
             renderer='templates/humans.pt')
def site_root_humans_view(request):
    """Site root humans.txt view"""
    request.response.content_type = 'text/plain'
    return {}


@view_config(name='sitemap.xml',
             context=ISiteRoot, request_type=IPyAMSUserLayer,
             renderer='templates/root-sitemap.pt')
class SiteRootSitemapView:
    """Site root sitemap view"""

    def __init__(self, request):
        self.request = request

    def __call__(self):
        self.request.response.content_type = 'text/xml'
        return {}

    @property
    def sources(self):
        """Sitemap sources"""
        timestamp = tztime(datetime.utcnow()).isoformat()
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            if not tool.shared_content_menu:
                continue
            publication_info = IWorkflowPublicationInfo(tool, None)
            if (publication_info is None) or publication_info.is_visible(self.request):
                yield timestamp, tool
        for name, adapter in self.request.registry.getAdapters(
                (self.request.context, self.request),
                ISitemapExtension):
            source = adapter.source
            if source is not None:
                yield timestamp, source


@view_config(name='sitemap.xml',
             context=IBaseSharedTool, request_type=IPyAMSUserLayer,
             renderer='templates/tool-sitemap.pt')
class SharedToolSitemapView:
    """Shared tool sitemap view"""

    def __init__(self, request):
        self.request = request

    def __call__(self):
        self.request.response.content_type = 'text/xml'
        return {}

    @property
    def contents(self):
        """Sitemap contents getter"""
        context = self.request.context
        catalog = get_utility(ICatalog)
        intids = get_utility(IIntIds)
        workflow = IWorkflow(context)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = Eq(catalog['parents'], intids.register(context)) & \
            Any(catalog['content_type'], vocabulary.by_value.keys()) & \
            Any(catalog['workflow_state'], workflow.visible_states)
        for version in unique_iter(CatalogResultSet(CatalogQuery(catalog).query(params))):
            yield from product(II18nManager(version).get_languages(), (version,))
