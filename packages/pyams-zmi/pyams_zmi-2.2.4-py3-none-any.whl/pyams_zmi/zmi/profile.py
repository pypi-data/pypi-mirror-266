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

"""PyAMS_zmi.zmi.profile module

This module provides components used for user profile management.
"""

from zope.interface import Interface, implementer

from pyams_form.ajax import AJAXFormRenderer, ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IFormContent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_table.interfaces import ITable
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_zmi.form import AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.configuration import IZMIConfiguration
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.profile import IUserProfile
from pyams_zmi.interfaces.table import ITableAttributes
from pyams_zmi.zmi.interfaces import IUserProfileEditForm

__docformat__ = 'restructuredtext'

from pyams_zmi import _


@ajax_form_config(name='user-profile.html',
                  layer=IPyAMSLayer)
@implementer(IUserProfileEditForm)
class UserProfileEditForm(AdminModalEditForm):
    """User profile edit form"""

    subtitle = _("User profile")
    legend = _("My user profile")
    modal_class = 'modal-xl'

    @property
    def fields(self):
        fields = Fields(IUserProfile)
        if not IZMIConfiguration(self.request.root).user_bundle_selection:
            fields = fields.omit('zmi_bundle')
        return fields

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        bundle = self.widgets.get('zmi_bundle')
        if bundle is not None:
            bundle.no_value_message = _("Use default theme")


@adapter_config(required=(Interface, IPyAMSLayer, UserProfileEditForm),
                provides=IFormContent)
def user_profile_edit_form_content(context, request, form):
    """User profile edit form content getter"""
    return IUserProfile(request.principal)


@adapter_config(required=(Interface, IAdminLayer, UserProfileEditForm),
                provides=IFormTitle)
def user_profile_edit_form_title(context, request, form):
    """User profile edit form title"""
    return request.principal.title


@adapter_config(required=(Interface, IAdminLayer, IUserProfileEditForm),
                provides=IAJAXFormRenderer)
class UserProfileEditFormRenderer(AJAXFormRenderer):
    """User profile edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes:
            return {
                'status': 'redirect'
            }
        return super().render(changes)


@adapter_config(name='profile',
                required=(Interface, IAdminLayer, ITable),
                provides=ITableAttributes)
class UserProfileTableAttributesAdapter(ContextRequestViewAdapter):
    """User profile table attributes adapter"""

    def __new__(cls, context, request, view):
        if getattr(request, 'principal', None) is None:
            return None
        return ContextRequestViewAdapter.__new__(cls)

    def update_attributes(self, source: dict):
        """Update source attributes with selected profile length"""
        profile = IUserProfile(self.request, None)
        if profile is not None:
            source.setdefault('table', {}).update({
                'data-page-length': profile.tables_length
            })
