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

from pyams_content.shared.view import IViewQuery
from pyams_content.shared.view.interfaces.query import IViewQueryFilterExtension, IViewQueryParamsExtension, \
    IViewUserQuery


class IEsViewQuery(IViewQuery):
    """Elasticsearch view query marker interface

    This is the base interface of view query.
    """


class IEsViewQueryParamsExtension(IViewQueryParamsExtension):
    """Elasticsearch view query params extension

    This interface is used to register custom adapters which are defined to get
    Elasticsearch query extra parameters.
    """


class IEsViewQueryFilterExtension(IViewQueryFilterExtension):
    """Elasticsearch view query filter extension

    This interface is used to register adapters which are defined to
    filter results of Elasticsearch query. So unlike params extensions,
    """


class IEsViewUserQuery(IViewUserQuery):
    """Elasticsearch view user query interface"""
