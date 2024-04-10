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

"""PyAMS_content.feature.search.portlet.skin.interfaces module

"""

from collections import OrderedDict
from enum import Enum

from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Attribute, Interface
from zope.schema import Bool, Choice, Int
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_i18n.schema import I18nTextLineField
from pyams_skin.schema import BootstrapThumbnailsSelectionField

__docformat__ = 'restructuredtext'

from pyams_content import _


SEARCH_RESULTS_RENDERER_SETTINGS_KEY = 'pyams_content.search.renderer::search-results'


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


class ISearchResultsPortletBaseRendererSettings(Interface):
    """Search results portlet renderer base settings interface"""

    display_if_empty = Bool(title=_("Display if empty?"),
                            description=_("If 'no', and if no result is found, the portlet "
                                          "will not display anything"),
                            required=True,
                            default=True)

    display_results_count = Bool(title=_("Display results count?"),
                                 description=_("If 'no', results count will not be displayed"),
                                 required=True,
                                 default=True)

    allow_sorting = Bool(title=_("Allow results sorting?"),
                         description=_("If 'no', results will not be sortable"),
                         required=True,
                         default=True)

    allow_pagination = Bool(title=_("Allow pagination?"),
                            description=_("If 'no', results will not be paginated"),
                            required=True,
                            default=True)

    header_display_mode = Choice(title=_("Header display mode"),
                                 description=_("Defines how results headers will be rendered"),
                                 required=True,
                                 vocabulary=HEADER_DISPLAY_MODES_VOCABULARY,
                                 default=HEADER_DISPLAY_MODE.FULL.value)

    start_length = Int(title=_("Start length"),
                       description=_("If you choose to display only header start, you can "
                                     "specify maximum text length"),
                       required=True,
                       default=120)

    display_illustrations = Bool(title=_("Display illustrations?"),
                                 description=_("If 'no', view contents will not display "
                                               "illustrations"),
                                 required=True,
                                 default=True)

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display images thumbnails"),
        default_selection='pano',
        change_selection=True,
        default_width=3,
        change_width=True,
        required=False)


class ISearchResultsPortletDefaultRendererSettings(ISearchResultsPortletBaseRendererSettings):
    """Search results portlet default renderer settings interface"""


class ISearchResultsPortletPanelsRendererSettings(ISearchResultsPortletBaseRendererSettings):
    """Search results portlet panels renderer settings interface"""

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display images thumbnails"),
        default_selection='pano',
        change_selection=True,
        default_width=12,
        change_width=False,
        required=False)

    button_title = I18nTextLineField(title=_("Button's title"),
                                     description=_("Optional navigation button's title"),
                                     required=False)


class ISearchResultsPortletCardsRendererSettings(ISearchResultsPortletBaseRendererSettings):
    """Search results portlet cards renderer settings interface"""

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Thumbnails selection"),
        description=_("Selection used to display images thumbnails"),
        default_selection='pano',
        change_selection=True,
        default_width=12,
        change_width=False,
        required=False)

    button_title = I18nTextLineField(title=_("Button's title"),
                                     description=_("Optional navigation button's title"),
                                     required=False)


class ISearchResultsPortletMasonryCardsRendererSettings(ISearchResultsPortletCardsRendererSettings):
    """Search results portlet Masonry cards renderer settings interface"""


#
# Search results renderers interfaces
#

class ISearchResultTitle(Interface):
    """Search result title interface"""


class ISearchResultHeader(Interface):
    """Search result header interface"""


class ISearchResultURL(Interface):
    """Search result target URL interface"""


class ISearchResultRenderer(IContentProvider):
    """Search result renderer interface"""

    title = Attribute("Search result title")
    header = Attribute("Search result header")
    url = Attribute("Search result URL")
