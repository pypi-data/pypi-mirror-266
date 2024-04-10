#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zmi.zmi.viewlet.toolbar module

This module provides several viewlet managers, which are used to display a toolbar and
contextual actions on content views.
"""

from zope.interface import Interface

from pyams_skin.interfaces.view import IModalPage
from pyams_skin.viewlet.actions import ContextActionsViewletManager
from pyams_skin.viewlet.menu import DropdownMenu
from pyams_template.template import template_config
from pyams_viewlet.manager import TemplateBasedViewletManager, WeightOrderedViewletManager, \
    viewletmanager_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextActionsDropdownMenu, IContextAddingsViewletManager, \
    ISecondaryActionsViewletManager, IToolbarViewletManager


__docformat__ = 'restructuredtext'

from pyams_zmi import _


@viewletmanager_config(name='pyams.toolbar',
                       layer=IAdminLayer, view=Interface,
                       provides=IToolbarViewletManager)
@template_config(template='templates/toolbar.pt')
class ToolbarViewletManager(TemplateBasedViewletManager, WeightOrderedViewletManager):
    """Actions viewlet manager"""


@viewletmanager_config(name='pyams.toolbar',
                       layer=IAdminLayer, view=IModalPage,
                       provides=IToolbarViewletManager)
class ModalToolbarViewletManager(ToolbarViewletManager):
    """Modal page actions viewlet manager"""

    def _get_viewlets(self):
        return ()


@viewletmanager_config(name='pyams.context_addings',
                       layer=IAdminLayer, view=Interface,
                       manager=IToolbarViewletManager, weight=10,
                       provides=IContextAddingsViewletManager)
class AddingsViewletManager(DropdownMenu):
    """Custom addings menu"""

    label = _("Add...")
    status = 'primary'
    css_class = 'btn-sm'
    icon_class = 'fas fa-plus'


@viewletmanager_config(name='pyams.actions',
                       layer=IAdminLayer, view=Interface,
                       manager=IToolbarViewletManager, weight=999,
                       provides=IContextActionsDropdownMenu)
class ContextActionsDropdownMenu(DropdownMenu):
    """Custom context actions menu"""

    label = _("Actions")
    css_class = 'btn-sm'


@viewletmanager_config(name='pyams.secondary-actions',
                       layer=IAdminLayer, view=Interface,
                       manager=IToolbarViewletManager, weight=980,
                       provides=ISecondaryActionsViewletManager)
class SecondaryActionsViewletManager(ContextActionsViewletManager):
    """Secondary actions viewlet manager"""
