#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content.shared.view.portlet.skin module

This module defines several renderers of view items portlet.
"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_content.component.links import IInternalLink
from pyams_content.shared.view.portlet import IViewItemsPortletSettings
from pyams_content.shared.view.portlet.skin.interfaces import HEADER_DISPLAY_MODE, IViewItemTargetURL, \
    IViewItemsPortletHorizontalRendererSettings, IViewItemsPortletPanelsRendererSettings, \
    IViewItemsPortletVerticalRendererSettings
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.skin import PortletRenderer
from pyams_sequence.reference import InternalReferenceMixin
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.text import get_text_start
from pyams_utils.url import canonical_url, relative_url

__docformat__ = 'restructuredtext'

from pyams_content import _


class BaseViewItemsPortletRenderer(PortletRenderer):
    """Base view items portlet renderer"""

    @staticmethod
    def is_internal_link(link):
        """Internal link checker"""
        return IInternalLink.providedBy(link)

    def get_url(self, target):
        """Item URL getter"""
        target_url = self.request.registry.queryMultiAdapter((target, self.request),
                                                             IViewItemTargetURL)
        if target_url is not None:
            if target_url.target is None:
                return target_url.url
            target = target_url.target
        if self.settings.force_canonical_url:
            return canonical_url(target, self.request)
        return relative_url(target, self.request)

    def render(self, template_name=''):
        result = super().render(template_name)
        if self.settings.first_page_only:
            start = int(self.request.params.get('start', 0))
            if start:
                return ''
        return result


#
# Vertical list view items renderer
#

@factory_config(IViewItemsPortletVerticalRendererSettings)
class ViewItemsPortletVerticalRendererSettings(InternalReferenceMixin, Persistent, Contained):
    """View items portlet vertical renderer settings"""

    display_illustrations = FieldProperty(IViewItemsPortletVerticalRendererSettings['display_illustrations'])
    thumb_selection = FieldProperty(IViewItemsPortletVerticalRendererSettings['thumb_selection'])
    display_breadcrumbs = FieldProperty(IViewItemsPortletVerticalRendererSettings['display_breadcrumbs'])
    display_tags = FieldProperty(IViewItemsPortletVerticalRendererSettings['display_tags'])
    paginate = FieldProperty(IViewItemsPortletVerticalRendererSettings['paginate'])
    page_size = FieldProperty(IViewItemsPortletVerticalRendererSettings['page_size'])
    reference = FieldProperty(IViewItemsPortletVerticalRendererSettings['reference'])
    link_label = FieldProperty(IViewItemsPortletVerticalRendererSettings['link_label'])


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, IViewItemsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/view-list-vertical.pt', layer=IPyAMSLayer)
class ViewItemsPortletVerticalRenderer(BaseViewItemsPortletRenderer):
    """View items portlet vertical renderer"""

    label = _("Simple vertical list (default)")
    weight = 1

    settings_interface = IViewItemsPortletVerticalRendererSettings


#
# Horizontal list view items renderer
#

@factory_config(IViewItemsPortletHorizontalRendererSettings)
class ViewItemsPortletHorizontalRendererSettings(Persistent, Contained):
    """View items portlet horizontal renderer settings"""

    thumb_selection = FieldProperty(IViewItemsPortletHorizontalRendererSettings['thumb_selection'])


@adapter_config(name='horizontal',
                required=(IPortalContext, IPyAMSLayer, Interface, IViewItemsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/view-list-horizontal.pt', layer=IPyAMSLayer)
class ViewItemsPortletHorizontalRenderer(BaseViewItemsPortletRenderer):
    """View items portlet horizontal renderer"""

    label = _("Horizontal thumbnails list")
    weight = 10

    settings_interface = IViewItemsPortletHorizontalRendererSettings


#
# Panels view items renderer
#

@factory_config(IViewItemsPortletPanelsRendererSettings)
class ViewItemsPortletPanelsRendererSettings(Persistent, Contained):
    """View items portlet panels renderer settings"""

    display_illustrations = FieldProperty(IViewItemsPortletPanelsRendererSettings['display_illustrations'])
    thumb_selection = FieldProperty(IViewItemsPortletPanelsRendererSettings['thumb_selection'])
    paginate = FieldProperty(IViewItemsPortletPanelsRendererSettings['paginate'])
    page_size = FieldProperty(IViewItemsPortletPanelsRendererSettings['page_size'])
    header_display_mode = FieldProperty(IViewItemsPortletPanelsRendererSettings['header_display_mode'])
    start_length = FieldProperty(IViewItemsPortletPanelsRendererSettings['start_length'])


@adapter_config(name='panels',
                required=(IPortalContext, IPyAMSLayer, Interface, IViewItemsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/view-panels.pt', layer=IPyAMSLayer)
class ViewItemsPortletPanelsRenderer(BaseViewItemsPortletRenderer):
    """View items portlet panels renderer"""

    label = _("Three vertical panels with panoramic illustrations")
    weight = 30

    settings_interface = IViewItemsPortletPanelsRendererSettings

    def get_header(self, item):
        settings = self.renderer_settings
        display_mode = settings.header_display_mode
        if display_mode == HEADER_DISPLAY_MODE.HIDDEN.value:
            return ''
        header = II18n(item).query_attribute('header', request=self.request)
        if display_mode == HEADER_DISPLAY_MODE.START.value:
            header = get_text_start(header, settings.start_length)
        return header
