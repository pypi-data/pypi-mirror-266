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

"""PyAMS_content.reference module

"""

from persistent import Persistent
from pyramid.events import subscriber
from zope.component.interfaces import ISite
from zope.container.contained import Contained
from zope.container.folder import Folder
from zope.interface import implementer
from zope.lifecycleevent import IObjectAddedEvent
from zope.schema.fieldproperty import FieldProperty

from pyams_content.interfaces import MANAGE_SITE_ROOT_PERMISSION
from pyams_content.reference.interfaces import IReferenceInfo, IReferenceManager, IReferenceTable
from pyams_i18n.interfaces import II18nManager
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.traversing import get_parent


__docformat__ = 'restructuredtext'


@factory_config(IReferenceManager)
class ReferencesManager(Folder):
    """References tables container"""

    title = FieldProperty(IReferenceManager['title'])
    short_name = FieldProperty(IReferenceManager['short_name'])

    def __init__(self):
        super().__init__()
        self.title = {
            'en': 'References tables',
            'fr': 'Tables de références'
        }
        self.short_name = self.title.copy()


@subscriber(IObjectAddedEvent, context_selector=IReferenceManager)
def handle_added_references_manager(event):
    """Handle new references manager"""
    site = get_parent(event.object, ISite)
    registry = site.getSiteManager()
    if registry is not None:
        registry.registerUtility(event.object, IReferenceManager)


@implementer(IReferenceTable, II18nManager)
class ReferenceTable(Folder):
    """References table"""

    title = FieldProperty(IReferenceTable['title'])
    short_name = FieldProperty(IReferenceTable['short_name'])

    languages = FieldProperty(II18nManager['languages'])


@implementer(IReferenceInfo)
class ReferenceInfo(Persistent, Contained):
    """Reference record"""

    title = FieldProperty(IReferenceInfo['title'])
    short_name = FieldProperty(IReferenceInfo['short_name'])


@adapter_config(required=IReferenceInfo,
                provides=IViewContextPermissionChecker)
class ReferenceInfoPermissionChecker(ContextAdapter):
    """Reference info permission checker"""

    edit_permission = MANAGE_SITE_ROOT_PERMISSION
