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

"""PyAMS_zmi.rest module

This module defines PyAMS API documentation service.
"""

from cornice import Service
from cornice.service import get_services
from cornice_swagger import CorniceSwagger

from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_utils.rest import handle_cors_headers


__docformat__ = 'restructuredtext'


#
# Swagger API documentation access
#

swagger = Service(name='OpenAPI',
                  path='/__api__',
                  description="OpenAPI documentation")


@swagger.options(permission=VIEW_SYSTEM_PERMISSION)
def openapi_options(request):
    """OpenAPI OPTIONS verb handler"""
    return handle_cors_headers(request)


@swagger.get(permission=VIEW_SYSTEM_PERMISSION)
def openapi_specification(request):  # pylint: disable=unused-argument
    """OpenAPI specification"""
    doc = CorniceSwagger(get_services())
    doc.summary_docstrings = True
    return doc.generate('PyAMS', '1.0')
