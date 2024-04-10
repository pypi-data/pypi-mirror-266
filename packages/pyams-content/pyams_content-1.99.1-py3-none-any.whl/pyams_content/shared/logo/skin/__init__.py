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

"""PyAMS_*** module

"""

__docformat__ = 'restructuredtext'

from pyams_content.shared.view.portlet.skin import IViewItemTargetURL
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import ContextRequestAdapter, adapter_config


# @adapter_config(required=(IWfLogo, IPyAMSLayer),
#                 provides=IViewItemTargetURL)
# class LogoViewItemTarget(ContextRequestAdapter):
#     """Logo view item target getter"""
#
#     @property
#     def target(self):
#         """Logo target getter"""
#         return self.context.target
#
#     @property
#     def url(self):
#         """Logo URL getter"""
#         return self.context.url
