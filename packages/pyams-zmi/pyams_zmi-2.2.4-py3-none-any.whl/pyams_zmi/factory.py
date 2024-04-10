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

"""PyAMS_zmi.factory module

This module provides a few object factory adapters for interfaces defined into
PyAMS_utils package.
"""

from zope.interface import Interface

from pyams_form.interfaces import IObjectFactory
from pyams_form.interfaces.form import IForm
from pyams_form.interfaces.widget import IObjectWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import get_interface_name, get_object_factory
from pyams_utils.interfaces.proxy import IProxyInfo


__docformat__ = 'restructuredtext'


@adapter_config(name=get_interface_name(IProxyInfo),
                required=(Interface, IFormLayer, IForm, IObjectWidget),
                provides=IObjectFactory)
def proxy_info_factory(*args, **kwargs):
    """Proxy information object widget factory"""
    return get_object_factory(IProxyInfo)
