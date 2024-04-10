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

"""PyAMS_zmi.zmi.swagger module

This module defines components which can be used to access Swagger-UI interface.
"""

from zope.interface import implementer

from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.view import IInnerPage
from pyams_template.template import template_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.zmi.interfaces import IConfigurationMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_zmi import _


@viewlet_config(name='swagger-ui.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IConfigurationMenu, weight=100,
                permission=VIEW_SYSTEM_PERMISSION)
class SwaggerMenu(NavigationMenuItem):
    """Swagger-UI menu"""

    label = _("Swagger API")
    href = '#swagger-ui.html'


@pagelet_config(name='swagger-ui.html',
                context=ISiteRoot, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
@template_config(template='templates/swagger.pt', layer=IPyAMSLayer)
@implementer(IInnerPage)
class SwaggerView:
    """Swagger view"""
