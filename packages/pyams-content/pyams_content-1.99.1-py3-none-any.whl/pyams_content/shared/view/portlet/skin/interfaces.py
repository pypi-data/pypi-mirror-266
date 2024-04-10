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

"""PyAMS_content.shared.view.portlet.skin.interfaces module

This module defines interfaces of view items portlet renderers settings.
"""

from collections import OrderedDict
from enum import Enum

from zope.interface import Attribute, Interface
from zope.schema import Bool, Choice, Int
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_i18n.schema import I18nTextLineField
from pyams_sequence.interfaces import IInternalReference
from pyams_sequence.schema import InternalReferenceField
from pyams_skin.schema import BootstrapThumbnailsSelectionField

__docformat__ = 'restructuredtext'

from pyams_content import _


class IViewItemTargetURL(Interface):
    """View item target URL"""

    target = Attribute("Reference target")

    url = Attribute("Reference URL")


class HEADER_DISPLAY_MODE(Enum):
    """Header display modes"""
    FULL = 'full'
    START = 'start'
    HIDDEN = 'none'


HEADER_DISPLAY_MODES_NAMES = OrderedDict((
    (HEADER_DISPLAY_MODE.FULL, _("Display full header")),
    (HEADER_DISPLAY_MODE.START, _("Display only header start")),
    (HEADER_DISPLAY_MODE.HIDDEN, _("Hide header"))
), )


HEADER_DISPLAY_MODES_VOCABULARY = SimpleVocabulary([
    SimpleTerm(v.value, title=t)
    for v, t in HEADER_DISPLAY_MODES_NAMES.items()
])


class IViewItemsPortletVerticalRendererSettings(IInternalReference):
    """View items portlet vertical renderer settings interface"""

    display_illustrations = Bool(title=_("Display illustrations?"),
                                 description=_("If 'no', view contents will not display "
                                               "illustrations"),
                                 required=True,
                                 default=True)

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display images thumbnails"),
        default_width={
            'xs': 12,
            'sm': 12,
            'md': 4,
            'lg': 4,
            'xl': 4
        },
        required=False)

    display_breadcrumbs = Bool(title=_("Display breadcrumbs?"),
                               description=_("If 'no', view items breadcrumbs will not be "
                                             "displayed"),
                               required=True,
                               default=True)

    display_tags = Bool(title=_("Display tags?"),
                        description=_("If 'no', view items tags will not be displayed"),
                        required=True,
                        default=True)

    paginate = Bool(title=_("Paginate?"),
                    description=_("If 'no', results pagination will be disabled"),
                    required=True,
                    default=True)

    page_size = Int(title=_("Page size"),
                    description=_("Number of items per page, if pagination is enabled"),
                    required=False,
                    default=10)

    reference = InternalReferenceField(title=_("'See all' link target"),
                                       description=_("Internal reference to site or search "
                                                     "folder displaying full list of view's "
                                                     "contents"),
                                       required=False)

    link_label = I18nTextLineField(title=_("Link label"),
                                   description=_("Label of the link to full list page"),
                                   required=False)


class IViewItemsPortletHorizontalRendererSettings(Interface):
    """View items portlet horizontal renderer settings interface"""

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display images thumbnails"),
        default_width={
            'xs': 3,
            'sm': 3,
            'md': 2,
            'lg': 1,
            'xl': 1
        },
        required=True)


class IViewItemsPortletPanelsRendererSettings(Interface):
    """View items portlet panels renderer settings interface"""

    display_illustrations = Bool(title=_("Display illustrations?"),
                                 description=_("If 'no', view contents will not display "
                                               "illustrations"),
                                 required=True,
                                 default=True)

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display illustrations thumbnails"),
        default_selection='pano',
        default_width={
            'xs': 6,
            'sm': 6,
            'md': 4,
            'lg': 3,
            'xl': 2
        },
        required=True)

    paginate = Bool(title=_("Paginate?"),
                    description=_("If 'no', results pagination will be disabled"),
                    required=True,
                    default=True)

    page_size = Int(title=_("Page size"),
                    description=_("Number of items per page, if pagination is enabled"),
                    required=False,
                    default=9)

    header_display_mode = Choice(title=_("Header display mode"),
                                 description=_("Defines how results headers will be rendered"),
                                 required=True,
                                 vocabulary=HEADER_DISPLAY_MODES_VOCABULARY,
                                 default=HEADER_DISPLAY_MODE.FULL.value)

    start_length = Int(title=_("Start length"),
                       description=_("If you choose to display only header start, you can specify "
                                     "maximum text length"),
                       required=True,
                       default=120)
