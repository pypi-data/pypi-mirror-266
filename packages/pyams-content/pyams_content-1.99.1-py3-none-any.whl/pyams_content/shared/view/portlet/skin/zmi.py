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

"""PyAMS_*** module

"""

from zope.interface import Interface

from pyams_content.shared.view.portlet.skin import IViewItemsPortletPanelsRendererSettings
from pyams_form.field import Fields
from pyams_form.group import Group
from pyams_form.interfaces.form import IFormFields, IGroup
from pyams_portal.zmi.interfaces import IPortletRendererSettingsEditForm
from pyams_utils.adapter import adapter_config
from pyams_zmi.form import FormGroupChecker
from pyams_zmi.interfaces import IAdminLayer

__docformat__ = 'restructuredtext'

from pyams_content import _


@adapter_config(required=(IViewItemsPortletPanelsRendererSettings, IAdminLayer, IPortletRendererSettingsEditForm),
                provides=IFormFields)
def view_items_panels_renderer_settings_fields(context, request, form):
    return Fields(Interface)


@adapter_config(name='illustration',
                required=(IViewItemsPortletPanelsRendererSettings, IAdminLayer, IPortletRendererSettingsEditForm),
                provides=IGroup)
class ViewItemsPanelsRendererIllustrationSettingsGroup(FormGroupChecker):
    """View item portlet panels renderer illustration settings group"""

    fields = Fields(IViewItemsPortletPanelsRendererSettings).select('display_illustrations', 'thumb_selection')
    weight = 10


@adapter_config(name='header',
                required=(IViewItemsPortletPanelsRendererSettings, IAdminLayer, IPortletRendererSettingsEditForm),
                provides=IGroup)
class ViewItemsPanelsRendererHeaderSettingsGroup(Group):
    """View items portlet panels renderer header settings group"""

    legend = _("Header display")

    fields = Fields(IViewItemsPortletPanelsRendererSettings).select('header_display_mode', 'start_length')
    weight = 20


@adapter_config(name='pagination',
                required=(IViewItemsPortletPanelsRendererSettings, IAdminLayer, IPortletRendererSettingsEditForm),
                provides=IGroup)
class ViewItemsPanelsRendererPaginationSettingsGroup(FormGroupChecker):
    """View item portlet panels renderer pagination settings group"""

    fields = Fields(IViewItemsPortletPanelsRendererSettings).select('paginate', 'page_size')
    weight = 30
