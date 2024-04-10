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

"""PyAMS_content.component.illustration.skin module

This module provides base illustrations adapters.
"""

from zope.interface import Interface

from pyams_content.component.illustration import IBaseIllustrationTarget, IIllustration, \
    ILinkIllustration, ILinkIllustrationTarget
from pyams_content.component.links import IInternalLink
from pyams_content.interfaces import IBaseContent
from pyams_content.shared.common import ISharedContent
from pyams_content.skin.interfaces import IContentBannerIllustration, IContentNavigationIllustration
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import HIDDEN_RENDERER_NAME
from pyams_site.interfaces import ISiteRoot
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension


#
# Illustrations adapters
#

@adapter_config(required=(IInternalLink, IPyAMSLayer),
                provides=IContentNavigationIllustration)
@adapter_config(required=(IBaseIllustrationTarget, IPyAMSLayer),
                provides=IContentNavigationIllustration)
def base_content_navigation_illustration_factory(context, request):
    """Default content navigation illustration adapter"""
    illustration = ILinkIllustration(context, None)
    if not (illustration and illustration.has_data()):
        illustration = IIllustration(context, None)
        if IIllustration.providedBy(illustration) and \
                (illustration.renderer == HIDDEN_RENDERER_NAME):
            illustration = None
    if illustration and illustration.has_data():
        return illustration
    if IInternalLink.providedBy(context):
        target = context.get_target()
        if target is not None:
            illustration = request.registry.queryMultiAdapter((target, request),
                                                              IContentNavigationIllustration)
            if illustration and illustration.has_data():
                return illustration
    return None


@adapter_config(required=(ILinkIllustrationTarget, IPyAMSLayer),
                provides=IContentNavigationIllustration)
def link_content_navigation_illustration_factory(context, request):
    """Content navigation illustration adapter for basic link illustration targets"""
    illustration = ILinkIllustration(context, None)
    if illustration and illustration.has_data():
        return illustration


@adapter_config(required=(ISharedContent, IPyAMSLayer),
                provides=IContentNavigationIllustration)
def shared_content_illustration_factory(context, request):
    """Shared content illustration factory"""
    version = context.visible_version
    if version is not None:
        return request.registry.queryMultiAdapter((version, request),
                                                  IContentNavigationIllustration)
    return None


@adapter_config(name='pyams_illustration',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class PyAMSIllustrationTALESExtension(ContextRequestViewAdapter):
    """PyAMS navigation illustration TALES extension"""

    def render(self, context=None, name=''):
        if context is None:
            context = self.context
        return self.request.registry.queryMultiAdapter((context, self.request),
                                                       IContentNavigationIllustration,
                                                       name=name)


@adapter_config(required=(ISiteRoot, IPyAMSLayer),
                provides=IContentBannerIllustration)
@adapter_config(context=(IBaseContent, IPyAMSLayer),
                provides=IContentBannerIllustration)
def base_content_banner_illustration_factory(context, request):
    """Base content banner illustration adapter"""
    illustration = IIllustration(context, None)
    if illustration and illustration.has_data() and (illustration.renderer != HIDDEN_RENDERER_NAME):
        return illustration
    return None


@adapter_config(name='pyams_banner_illustration',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class PyAMSBannerIllustrationTALESExtension(ContextRequestViewAdapter):
    """PyAMS banner illustration TALES extension"""

    def render(self, context=None, name=''):
        if context is None:
            context = self.context
        return self.request.registry.queryMultiAdapter((context, self.request),
                                                       IContentBannerIllustration,
                                                       name=name)
