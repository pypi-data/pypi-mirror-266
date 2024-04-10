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

"""PyAMS_content.component.association.skin module

This module provides associations rendering components.
"""

from zope.interface import Interface

from pyams_content.component.association import IAssociationContainer
from pyams_content.component.association.interfaces import IAssociationInfo
from pyams_content.component.extfile import IExtFile
from pyams_content.component.links import IBaseLink
from pyams_layer.interfaces import IPyAMSLayer
from pyams_template.template import template_config
from pyams_viewlet.viewlet import ViewContentProvider, contentprovider_config


__docformat__ = 'restructuredtext'


class AssociationContainerRendererMixin:
    """Associations container renderer mixin"""

    attachments = None
    links = None

    def get_associations(self):
        """Associations getter"""
        yield from IAssociationContainer(self.context).get_visible_items(self.request)

    @staticmethod
    def get_link_info(item):
        """Association item information getter"""
        return IAssociationInfo(item)

    def update(self):
        super().update()
        self.attachments = []
        self.links = []
        for item in self.get_associations():
            if IExtFile.providedBy(item):
                self.attachments.append(item)
            elif IBaseLink.providedBy(item):
                self.links.append(item)


@contentprovider_config(name='pyams_content.associations',
                        layer=IPyAMSLayer, view=Interface)
@template_config(template='templates/association-viewlet.pt', layer=IPyAMSLayer)
class AssociationsViewlet(AssociationContainerRendererMixin, ViewContentProvider):
    """Associations viewlet"""
