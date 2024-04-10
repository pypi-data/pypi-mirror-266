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

"""PyAMS_zmi.utils module

This module provides a small set of generic components.
"""

from zope.location import ILocation

from pyams_utils.adapter import adapter_config, query_adapter
from pyams_utils.interfaces import MISSING_INFO
from pyams_zmi.interfaces import IObjectHint, IObjectIcon, IObjectLabel, IObjectName

__docformat__ = 'restructuredtext'


@adapter_config(required=ILocation,
                provides=IObjectName)
def location_name(context):
    """Basic location name factory"""
    return context.__name__


def get_object_name(context, request, view=None, name=''):
    """Get object name"""
    adapter = query_adapter(IObjectName, request, context, view, name)
    if name and (adapter is None):
        adapter = query_adapter(IObjectName, request, context, view)
    return adapter


@adapter_config(required=ILocation,
                provides=IObjectLabel)
def location_label(context):
    """Basic location name factory"""
    return MISSING_INFO


def get_object_label(context, request, view=None, name=''):
    """Get object label"""
    adapter = query_adapter(IObjectLabel, request, context, view, name)
    if name and (adapter is None):
        adapter = query_adapter(IObjectLabel, request, context, view)
    return adapter


@adapter_config(required=ILocation,
                provides=IObjectIcon)
def location_icon(context):  # pylint: disable=unused-argument
    """Basic location icon factory"""
    return 'far fa-square'


def get_object_icon(context, request, view=None, name=''):
    """Get object icon"""
    adapter = query_adapter(IObjectIcon, request, context, view, name)
    if name and (adapter is None):
        adapter = query_adapter(IObjectIcon, request, context, view)
    return adapter


def get_object_hint(context, request, view=None, name=''):
    """Get object hint"""
    adapter = query_adapter(IObjectHint, request, context, view, name)
    if name and (adapter is None):
        adapter = query_adapter(IObjectHint, request, context, view)
    return adapter
