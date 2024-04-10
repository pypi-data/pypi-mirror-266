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

"""PyAMS_content.workflow.zmi.publication module

"""

from datetime import datetime

from pyams_content.interfaces import MANAGE_SITE_PERMISSION
from pyams_content.shared.site.interfaces import IBaseSiteItem

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.timezone import tztime
from pyams_viewlet.viewlet import viewlet_config
from pyams_workflow.interfaces import IWorkflowPublicationInfo
from pyams_zmi.form import AdminEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IPropertiesMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_content import _


@viewlet_config(name='workflow-publication.menu',
                context=IBaseSiteItem, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=510,
                permission=MANAGE_SITE_PERMISSION)
class SiteItemPublicationDatesMenu(NavigationMenuItem):
    """Site item publication dates menu"""

    label = _("Publication dates")
    href = '#workflow-publication.html'


@ajax_form_config(name='workflow-publication.html',
                  context=IBaseSiteItem, layer=IPyAMSLayer,
                  permission=MANAGE_SITE_PERMISSION)
class SiteItemPublicationDatesEditForm(AdminEditForm):
    """Site item publication dates edit form"""

    title = _("Workflow management")
    legend = _("Content publication dates")

    fields = Fields(IWorkflowPublicationInfo).select('publication_effective_date',
                                                     'publication_expiration_date')

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        effective_date = self.widgets.get('publication_effective_date')
        if effective_date is not None:
            pub_info = IWorkflowPublicationInfo(self.context)
            if (pub_info is not None) and \
                    (pub_info.first_publication_date is None) and \
                    (pub_info.publication_effective_date is None):
                effective_date.value = tztime(datetime.utcnow())


@adapter_config(required=(IBaseSiteItem, IAdminLayer, SiteItemPublicationDatesEditForm),
                provides=IAJAXFormRenderer)
class SiteItemPublicationDatesEditFormRenderer(ContextRequestViewAdapter):
    """Site item publication dates edit form renderer"""

    def render(self, changes):
        """Changes renderer"""
        if not changes:
            return None
        return {
            'status': 'reload'
        }
