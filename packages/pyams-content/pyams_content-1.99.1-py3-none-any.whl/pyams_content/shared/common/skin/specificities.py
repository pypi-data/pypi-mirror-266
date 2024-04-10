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

"""PyAMS_content.shared.common.skin.specificities module

This module defines a custom content provider used for shared contents specificities
rendering.
"""

from zope.interface import Interface

from pyams_content.shared.common.portlet.interfaces import ISpecificitiesRenderer
from pyams_layer.interfaces import IPyAMSUserLayer
from pyams_viewlet.viewlet import ViewContentProvider, contentprovider_config

__docformat__ = 'restructuredtext'


@contentprovider_config(name='pyams_content.specificities',
                        layer=IPyAMSUserLayer, view=Interface)
class SharedContentSpecificitiesContentProvider(ViewContentProvider):
    """Shared content specificities content provider"""

    renderer = None

    def update(self, name=''):
        super().update()
        registry = self.request.registry
        renderer = registry.queryMultiAdapter((self.context, self.request, self.view),
                                              ISpecificitiesRenderer,
                                              name=name)
        if renderer is not None:
            renderer.update()
            self.renderer = renderer

    def render(self, template_name=''):
        if self.renderer is None:
            return ''
        return self.renderer.render(template_name)
