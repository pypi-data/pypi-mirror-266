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

"""PyAMS_content.reference.pictogram module

"""

__docformat__ = 'restructuredtext'

from pyramid.events import subscriber
from zope.component.interfaces import ISite
from zope.lifecycleevent import IObjectAddedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_content.reference import ReferenceInfo, ReferenceTable
from pyams_content.reference.pictogram.interfaces import IPictogram, IPictogramTable, \
    PICTOGRAM_VOCABULARY
from pyams_file.property import I18nFileProperty
from pyams_i18n.interfaces import II18n
from pyams_utils.factory import factory_config
from pyams_utils.registry import query_utility
from pyams_utils.request import check_request
from pyams_utils.traversing import get_parent
from pyams_utils.vocabulary import vocabulary_config


@factory_config(IPictogramTable)
class PictogramTable(ReferenceTable):
    """Pictogram table"""


@subscriber(IObjectAddedEvent, context_selector=IPictogramTable)
def handle_added_pictogram_table(event):
    """Handle new pictogram table"""
    site = get_parent(event.object, ISite)
    registry = site.getSiteManager()
    if registry is not None:
        registry.registerUtility(event.object, IPictogramTable)


@factory_config(IPictogram)
class Pictogram(ReferenceInfo):
    """Pictogram persistent class"""

    image = I18nFileProperty(IPictogram['image'])
    alt_title = FieldProperty(IPictogram['alt_title'])
    header = FieldProperty(IPictogram['header'])


@vocabulary_config(name=PICTOGRAM_VOCABULARY)
class PictogramsVocabulary(SimpleVocabulary):
    """Pictograms vocabulary"""

    def __init__(self, context=None):
        table = query_utility(IPictogramTable)
        if table is not None:
            request = check_request()
            terms = [
                SimpleTerm(v.__name__,
                           title=II18n(v).query_attribute('title', request=request))
                for v in table.values()
            ]
        else:
            terms = []
        super(PictogramsVocabulary, self).__init__(terms)
