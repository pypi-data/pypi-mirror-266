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

"""PyAMS_content.feature.search.portlet.skin module

"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface, implementer
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty

from pyams_content.feature.search.portlet import ISearchResultsPortletSettings
from pyams_content.feature.search.portlet.skin.interfaces import HEADER_DISPLAY_MODE, ISearchResultHeader, \
    ISearchResultRenderer, ISearchResultURL, ISearchResultTitle, ISearchResultsPortletBaseRendererSettings, \
    ISearchResultsPortletCardsRendererSettings, ISearchResultsPortletDefaultRendererSettings, \
    ISearchResultsPortletMasonryCardsRendererSettings, ISearchResultsPortletPanelsRendererSettings
from pyams_content.shared.common import IWfSharedContent
from pyams_content.skin.interfaces import ISearchResultsCardsView, ISearchResultsPanelsView, ISearchResultsView
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer, IPyAMSUserLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.skin import PortletRenderer
from pyams_skin.interfaces.viewlet import IBreadcrumbs
from pyams_template.template import template_config
from pyams_utils.adapter import NullAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.text import get_text_start
from pyams_utils.url import canonical_url, relative_url

__docformat__ = 'restructuredtext'

from pyams_content import _
from pyams_viewlet.viewlet import ViewContentProvider


class SearchResultsPortletBaseRendererSettings(Persistent, Contained):
    """Search results portlet base renderer settings"""

    display_if_empty = FieldProperty(
        ISearchResultsPortletBaseRendererSettings['display_if_empty'])
    display_results_count = FieldProperty(
        ISearchResultsPortletBaseRendererSettings['display_results_count'])
    allow_sorting = FieldProperty(ISearchResultsPortletBaseRendererSettings['allow_sorting'])
    allow_pagination = FieldProperty(ISearchResultsPortletBaseRendererSettings['allow_pagination'])
    header_display_mode = FieldProperty(
        ISearchResultsPortletBaseRendererSettings['header_display_mode'])
    start_length = FieldProperty(ISearchResultsPortletBaseRendererSettings['start_length'])
    display_illustrations = FieldProperty(ISearchResultsPortletBaseRendererSettings['display_illustrations'])
    thumb_selection = FieldProperty(ISearchResultsPortletBaseRendererSettings['thumb_selection'])


@implementer(ISearchResultsView)
class SearchResultsPortletBaseRenderer(PortletRenderer):
    """Search results portlet base renderer"""

    default_page_length = 10
    current_page_length = None

    def update(self):
        params = self.request.params
        settings = self.renderer_settings
        if not settings.allow_pagination:
            self.current_page_length = '999'
        elif 'length' in params:
            self.current_page_length = str(params.get('length'))
        else:
            self.current_page_length = str(self.default_page_length)
        super().update()

    def render_item(self, item):
        renderer = self.request.registry.queryMultiAdapter((item, self.request, self),
                                                           ISearchResultRenderer)
        if renderer is not None:
            renderer.update()
            return renderer.render()
        return ''


#
# Default search results portlet renderer
#

@factory_config(ISearchResultsPortletDefaultRendererSettings)
class SearchResultsPortletDefaultRendererSettings(SearchResultsPortletBaseRendererSettings):
    """Search results portlet default renderer settings"""

    thumb_selection = FieldProperty(ISearchResultsPortletDefaultRendererSettings['thumb_selection'])


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, ISearchResultsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/search-default.pt', layer=IPyAMSLayer)
class SearchResultsPortletDefaultRenderer(SearchResultsPortletBaseRenderer):
    """Search results portlet default renderer"""

    label = _("Paginated search results (default)")
    weight = 1

    settings_interface = ISearchResultsPortletDefaultRendererSettings


#
# Panels search results portlet renderer
#

@factory_config(ISearchResultsPortletPanelsRendererSettings)
class SearchResultsPortletPanelsRendererSettings(SearchResultsPortletBaseRendererSettings):
    """Search results portlet panels renderer settings"""

    thumb_selection = FieldProperty(ISearchResultsPortletPanelsRendererSettings['thumb_selection'])
    button_title = FieldProperty(ISearchResultsPortletPanelsRendererSettings['button_title'])


@adapter_config(name='panels',
                required=(IPortalContext, IPyAMSLayer, Interface, ISearchResultsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/search-panels.pt', layer=IPyAMSLayer)
@implementer(ISearchResultsPanelsView)
class SearchResultsPortletPanelsRenderer(SearchResultsPortletBaseRenderer):
    """Search results portlet panels renderer"""

    label = _("Paneled search results")
    weight = 10

    settings_interface = ISearchResultsPortletPanelsRendererSettings


#
# Cards search results portlet renderer
#

@factory_config(ISearchResultsPortletCardsRendererSettings)
class SearchResultsPortletCardsRendererSettings(SearchResultsPortletBaseRendererSettings):
    """Search results portlet cards renderer settings"""

    thumb_selection = FieldProperty(ISearchResultsPortletCardsRendererSettings['thumb_selection'])
    button_title = FieldProperty(ISearchResultsPortletCardsRendererSettings['button_title'])


@adapter_config(name='cards',
                required=(IPortalContext, IPyAMSLayer, Interface, ISearchResultsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/search-cards.pt', layer=IPyAMSLayer)
@implementer(ISearchResultsCardsView)
class SearchResultsPortletCardsRenderer(SearchResultsPortletBaseRenderer):
    """Search results portlet cards renderer"""

    label = _("Bootstrap cards search results")
    weight = 20

    settings_interface = ISearchResultsPortletCardsRendererSettings


#
# Masonry cards search results portlet renderer
#

@factory_config(ISearchResultsPortletMasonryCardsRendererSettings)
class SearchResultsPortletMasonryCardsRendererSettings(SearchResultsPortletCardsRendererSettings):
    """Search results portlet Masonry cards renderer settings"""


@adapter_config(name='cards::masonry',
                required=(IPortalContext, IPyAMSLayer, Interface, ISearchResultsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/search-cards-masonry.pt', layer=IPyAMSLayer)
@implementer(ISearchResultsCardsView)
class SearchResultsPortletMasonryCardsRenderer(SearchResultsPortletBaseRenderer):
    """Search results portlet Masonry cards renderer"""

    label = _("Bootstrap Masonry cards search results")
    weight = 30

    settings_interface = ISearchResultsPortletMasonryCardsRendererSettings


#
# Search results adapters
#

@adapter_config(context=(ILocation, IPyAMSUserLayer, ISearchResultsView),
                provides=IBreadcrumbs)
class LocationBreadcrumbsAdapter(NullAdapter):
    """Disable breadcrumbs in search results view"""


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsView),
                provides=ISearchResultTitle)
def shared_content_result_title_adapter(context, request, view):
    """Shared content result title adapter"""
    return II18n(context).query_attribute('title', request=request)


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsView),
                provides=ISearchResultHeader)
def shared_content_result_header_adapter(context, request, view):
    """Shared content result header adapter"""
    return II18n(context).query_attribute('header', request=request)


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsView),
                provides=ISearchResultURL)
def shared_content_result_target_adapter(context, request, view):
    """Shared content result target URL adapter"""
    if view.settings.force_canonical_url:
        return canonical_url(context, request)
    return relative_url(context, request)


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsView),
                provides=ISearchResultRenderer)
@template_config(template='templates/search-result.pt', layer=IPyAMSUserLayer)
class WfSharedContentSearchResultRenderer(ViewContentProvider):
    """Shared content search result renderer"""

    @property
    def title(self):
        return self.request.registry.queryMultiAdapter((self.context, self.request, self.view),
                                                       ISearchResultTitle)

    @property
    def header(self):
        display_mode = HEADER_DISPLAY_MODE.FULL.value
        settings = self.view.renderer_settings
        if ISearchResultsPortletBaseRendererSettings.providedBy(settings):
            display_mode = settings.header_display_mode
        if display_mode == HEADER_DISPLAY_MODE.HIDDEN.value:
            return ''
        header = self.request.registry.queryMultiAdapter((self.context, self.request, self.view),
                                                         ISearchResultHeader)
        if display_mode == HEADER_DISPLAY_MODE.START.value:
            header = get_text_start(header, settings.start_length)
        return header

    @property
    def url(self):
        return self.request.registry.queryMultiAdapter((self.context, self.request, self.view),
                                                       ISearchResultURL)


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsPanelsView),
                provides=ISearchResultRenderer)
@template_config(template='templates/search-panel.pt', layer=IPyAMSUserLayer)
class WfSharedContentSearchResultPanelRenderer(WfSharedContentSearchResultRenderer):
    """Shared content search result panel renderer"""


@adapter_config(context=(IWfSharedContent, IPyAMSUserLayer, ISearchResultsCardsView),
                provides=ISearchResultRenderer)
@template_config(template='templates/search-card.pt', layer=IPyAMSUserLayer)
class WfSharedContentSearchResultCardRenderer(WfSharedContentSearchResultRenderer):
    """Shared content search result card renderer"""
