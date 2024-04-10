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

"""PyAMS_content_es.component.extfile module

This module defines adapters which are used to handle external file indexation.
"""

__docformat__ = 'restructuredtext'

import base64

from pyams_content.component.association.interfaces import IAssociationContainer, IAssociationItem
from pyams_content.component.extfile.interfaces import IBaseExtFile
from pyams_content.component.paragraph.interfaces import IParagraphContainer, \
    IParagraphContainerTarget
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config
from pyams_workflow.interfaces import IWorkflow, IWorkflowState


@adapter_config(name='extfile',
                required=IParagraphContainerTarget,
                provides=IDocumentIndexInfo)
def paragraph_container_extfile_index_info(context):
    """Paragraph container external file indexation info"""

    workflow_state = None
    workflow = IWorkflow(context, None)
    if workflow is not None:
        workflow_state = IWorkflowState(context, None)

    # extract paragraphs attachments
    extfiles = []
    attachments = []
    for paragraph in IParagraphContainer(context).get_visible_paragraphs():
        associations = IAssociationContainer(paragraph, {})
        for extfile in associations.values():
            if not IAssociationItem(extfile).visible:
                continue
            if not (IBaseExtFile.providedBy(extfile) and extfile.data):
                continue
            extfiles.append({
                'title': extfile.title,
                'description': extfile.description
            })
            # don't index attachments for contents which are not published
            if workflow_state and (workflow_state.state not in workflow.visible_states):
                continue
            for lang, data in extfile.data.items():
                content_type = data.content_type
                if isinstance(content_type, bytes):
                    content_type = content_type.decode()
                if content_type.startswith('image/') or \
                        content_type.startswith('audio/') or \
                        content_type.startswith('video/'):
                    continue
                attachments.append({
                    'content_type': content_type,
                    'name': data.filename,
                    'language': lang,
                    'content': base64.encodebytes(data.data).decode().replace('\n', '')
                })
    result = {
        'extfile': extfiles
    }
    if attachments:
        result.update({
            '__pipeline__': 'attachment',
            'attachments': attachments
        })
    return result
