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

"""PyAMS_content_es.component.links module

This module defines the adapters which are used to handle links indexation.
"""

from pyams_content.component.association.interfaces import IAssociationContainer, IAssociationItem
from pyams_content.component.links import IBaseLink
from pyams_content.component.paragraph.interfaces import IParagraphContainer, \
    IParagraphContainerTarget
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@adapter_config(name='links',
                required=IParagraphContainerTarget,
                provides=IDocumentIndexInfo)
def paragraph_container_target_link_index_info(context):
    """Internal and external links index info"""
    links = []
    for paragraph in IParagraphContainer(context).get_visible_paragraphs():
        associations = IAssociationContainer(paragraph, {})
        for link in associations.values():
            if not IAssociationItem(link).visible:
                continue
            if not IBaseLink.providedBy(link):
                continue
            links.append({
                'title': link.title,
                'description': link.description
            })
    return {
        'link': links
    }
