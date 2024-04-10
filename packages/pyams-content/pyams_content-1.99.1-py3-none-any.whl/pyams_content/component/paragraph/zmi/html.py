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

"""PyAMS_content.component.paragraph.zmi.html module

This module provides management interface components for raw source code and rich text
paragraphs.
"""

from pyramid.events import subscriber
from zope.interface import alsoProvides

from pyams_content.component.paragraph import IParagraphContainer, IParagraphContainerTarget
from pyams_content.component.paragraph.interfaces.html import HTML_PARAGRAPH_ICON_CLASS, \
    HTML_PARAGRAPH_NAME, HTML_PARAGRAPH_TYPE, IHTMLParagraph, IRawParagraph, \
    RAW_PARAGRAPH_ICON_CLASS, RAW_PARAGRAPH_NAME, RAW_PARAGRAPH_TYPE
from pyams_content.component.paragraph.zmi import BaseParagraphAddForm, BaseParagraphAddMenu
from pyams_content.component.paragraph.zmi.interfaces import IParagraphContainerBaseTable
from pyams_form.ajax import ajax_form_config
from pyams_form.interfaces.form import IFormUpdatedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import DEFAULT_RENDERER_NAME, HIDDEN_RENDERER_NAME
from pyams_utils.interfaces.data import IObjectData
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.form import IPropertiesEditForm
from pyams_zmi.interfaces.viewlet import IContextAddingsViewletManager

__docformat__ = 'restructuredtext'


#
# Raw paragraphs forms
#

@viewlet_config(name='add-raw-paragraph.menu',
                context=IParagraphContainerTarget, layer=IAdminLayer,
                view=IParagraphContainerBaseTable,
                manager=IContextAddingsViewletManager, weight=900)
class RawParagraphAddMenu(BaseParagraphAddMenu):
    """Raw paragraph add menu"""

    label = RAW_PARAGRAPH_NAME
    icon_class = RAW_PARAGRAPH_ICON_CLASS

    factory_name = RAW_PARAGRAPH_TYPE
    href = 'add-raw-paragraph.html'


@ajax_form_config(name='add-raw-paragraph.html',
                  context=IParagraphContainer, layer=IPyAMSLayer)
class RawParagraphAddForm(BaseParagraphAddForm):
    """Raw paragraph add form"""

    content_factory = IRawParagraph


@subscriber(IFormUpdatedEvent,
            form_selector=RawParagraphAddForm)
@subscriber(IFormUpdatedEvent,
            form_selector=IPropertiesEditForm,
            context_selector=IRawParagraph)
def handle_raw_paragraph_form_update(event):
    """Handle raw paragraph form update"""
    body = event.form.widgets.get('body')
    if body is not None:
        body.add_widgets_class('height-100')
        body.widget_css_class = 'editor height-300px'
        filename = 'body.html'
        if IPropertiesEditForm.providedBy(event.form):
            context = event.form.context
            if context.renderer not in (HIDDEN_RENDERER_NAME, DEFAULT_RENDERER_NAME):
                renderer = context.get_renderer()
                if renderer is not None:
                    filename = renderer.editor_filename
        for widget in body.widgets.values():
            widget.object_data = {
                'ams-filename': filename
            }
            alsoProvides(widget, IObjectData)


#
# HTML paragraphs forms
#

@viewlet_config(name='add-html-paragraph.menu',
                context=IParagraphContainerTarget, layer=IAdminLayer,
                view=IParagraphContainerBaseTable,
                manager=IContextAddingsViewletManager, weight=50)
class HTMLParagraphAddMenu(BaseParagraphAddMenu):
    """HTML paragraph add menu"""

    label = HTML_PARAGRAPH_NAME
    icon_class = HTML_PARAGRAPH_ICON_CLASS

    factory_name = HTML_PARAGRAPH_TYPE
    href = 'add-html-paragraph.html'


@ajax_form_config(name='add-html-paragraph.html',
                  context=IParagraphContainer, layer=IPyAMSLayer)
class HTMLParagraphAddForm(BaseParagraphAddForm):
    """HTML rich text paragraph add form"""

    content_factory = IHTMLParagraph
