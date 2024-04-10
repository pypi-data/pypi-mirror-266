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

"""PyAMS_content.common.zmi.manager module

This module defines common management components for shared content managers.
"""

from zope.interface import Interface

from pyams_content.interfaces import IBaseContent, MANAGE_TOOL_PERMISSION
from pyams_content.shared.common import IBaseSharedTool
from pyams_content.shared.common.interfaces import ISharedTool
from pyams_content.shared.common.manager import BaseSharedTool
from pyams_content.zmi.properties import PropertiesEditForm
from pyams_form.ajax import AJAXFormRenderer, ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_i18n.interfaces import II18n
from pyams_i18n_views.zmi.manager import I18nManagerLanguagesEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_skin.interfaces.viewlet import IBreadcrumbItem
from pyams_skin.viewlet.breadcrumb import BreadcrumbItem
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_viewlet.manager import viewletmanager_config
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.viewlet import IMenuHeader, IPropertiesMenu, ISiteManagementMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_content import _


@adapter_config(required=(ISharedTool, IAdminLayer, Interface),
                provides=IObjectLabel)
def shared_tool_label(context, request, view):
    """Shared tool label"""
    return II18n(context).query_attribute('title', request=request)


@adapter_config(required=(ISharedTool, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class SharedToolBreadcrumb(BreadcrumbItem):
    """Shared tool breadcrumb item"""

    @property
    def label(self):
        return II18n(self.context).query_attribute('short_name', request=self.request)

    view_name = 'admin'
    css_class = 'breadcrumb-item persistent strong'


@adapter_config(required=(ISharedTool, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def shared_tool_menu_header(context, request, view, menu):
    """Shared tool management menu header"""
    return request.localizer.translate(_("Shared content management"))


@viewletmanager_config(name='properties.menu',
                       context=ISharedTool, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=10,
                       provides=IPropertiesMenu,
                       permission=VIEW_SYSTEM_PERMISSION)
class SharedToolPropertiesMenu(NavigationMenuItem):
    """Shared tool properties menu"""

    label = _("Properties")
    icon_class = 'fas fa-edit'
    href = '#properties.html'


@ajax_form_config(name='properties.html',
                  context=ISharedTool, layer=IPyAMSLayer,
                  permission=VIEW_SYSTEM_PERMISSION)
class SharedToolPropertiesEditForm(PropertiesEditForm):
    """Shared tool properties edit form"""

    title = _("Shared tool properties")
    legend = _("Main tool properties")

    fields = Fields(IBaseSharedTool).omit('__name__', '__parent__')


@adapter_config(required=(ISharedTool, IAdminLayer, SharedToolPropertiesEditForm),
                provides=IAJAXFormRenderer)
class SharedToolPropertiesEditFormRenderer(AJAXFormRenderer):
    """Shared tool properties edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        if 'title' in changes.get(IBaseContent, ()):
            return {
                'status': 'reload',
                'message': self.request.localizer.translate(self.form.success_message)
            }
        return super().render(changes)


@adapter_config(required=(BaseSharedTool, IPyAMSLayer, I18nManagerLanguagesEditForm),
                provides=IViewContextPermissionChecker)
class SharedToolLanguagesEditFormPermissionChecker(ContextRequestViewAdapter):
    """Shared tool languages edit form permission checker"""

    edit_permission = MANAGE_TOOL_PERMISSION
