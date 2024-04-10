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

"""PyAMS_zmi.zmi.environment module

This module is used to display running version of all installed packages.
"""

import os

from pyams_utils.list import unique

try:
    from importlib.metadata import distributions
except ImportError:
    from importlib_metadata import distributions

from pyramid.decorator import reify

from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_table.interfaces import IColumn
from pyams_utils.adapter import adapter_config
from pyams_viewlet.viewlet import ViewContentProvider, viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.table import IInnerTable
from pyams_zmi.table import InnerTableAdminView, MultipleTablesAdminView, NameColumn, Table
from pyams_zmi.zmi.interfaces import IConfigurationMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_zmi import _


@viewlet_config(name='environment.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IConfigurationMenu, weight=50,
                permission=MANAGE_SYSTEM_PERMISSION)
class EnvironmentMenu(NavigationMenuItem):
    """Environment menu"""

    label = _("Environment")
    href = '#environment.html'


@pagelet_config(name='environment.html',
                context=ISiteRoot, layer=IPyAMSLayer,
                permission=MANAGE_SYSTEM_PERMISSION)
class EnvironmentView(MultipleTablesAdminView):
    """Environment view"""

    table_label = _("Application runtime environment")


#
# Packages versions
#

class PackagesVersionsTable(Table):
    """Packages versions table"""

    def __init__(self, context, request):
        super().__init__(context, request)
        if distributions is not None:
            self.distributions = distributions()
        else:
            environment = self.environment = Environment()
            environment.scan()

    @reify
    def id(self):
        return '{}_packages'.format(super().id)

    @reify
    def values(self):
        if distributions is not None:
            return unique(self.distributions,
                          key=lambda x: x.name)
        return self.environment


@adapter_config(name='package-name',
                required=(ISiteRoot, IAdminLayer, PackagesVersionsTable),
                provides=IColumn)
class PackagesNameColumn(NameColumn):
    """Package name column"""

    i18n_header = _("Package name")
    weight = 10

    def get_value(self, obj):
        """Value getter"""
        if distributions is not None:
            return obj.name
        environment = self.table.values
        return environment[obj][0].project_name


@adapter_config(name='package-version',
                required=(ISiteRoot, IAdminLayer, PackagesVersionsTable),
                provides=IColumn)
class PackageVersionColumn(NameColumn):
    """Package version column"""

    i18n_header = _("Version")
    weight = 20

    def get_value(self, obj):
        """Value getter"""
        return obj.version


@adapter_config(name='package-path',
                required=(ISiteRoot, IAdminLayer, PackagesVersionsTable),
                provides=IColumn)
class PackagePathColumn(NameColumn):
    """Package path column"""

    i18n_header = _("Path")
    weight = 30

    def get_value(self, obj):
        """Value getter"""
        if distributions is not None:
            return str(obj.locate_file(''))
        environment = self.table.values
        return environment[obj][0].location


@adapter_config(name='packages-versions',
                required=(ISiteRoot, IAdminLayer, EnvironmentView),
                provides=IInnerTable)
class PackagesVersionsView(InnerTableAdminView, ViewContentProvider):
    """Packages versions view"""

    table_class = PackagesVersionsTable
    table_label = _("Packages versions")

    hide_section = True

    weight = 10


#
# Environment variables
#

class EnvironmentTable(Table):
    """Environment table"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.environ = os.environ

    @reify
    def id(self):
        return '{}_environ'.format(super().id)

    @reify
    def values(self):
        return self.environ


@adapter_config(name='setting-name',
                required=(ISiteRoot, IAdminLayer, EnvironmentTable),
                provides=IColumn)
class EnvironmentNameColumn(NameColumn):
    """Environment name column"""

    i18n_header = _("Variable name")
    weight = 10

    def get_value(self, obj):
        """Value getter"""
        return obj


@adapter_config(name='environ-value',
                required=(ISiteRoot, IAdminLayer, EnvironmentTable),
                provides=IColumn)
class EnvironmentValueColumn(NameColumn):
    """Environment value column"""

    i18n_header = _("Value")
    weight = 20

    def get_value(self, obj):
        """Value getter"""
        environ = self.table.environ
        return environ.get(obj)


@adapter_config(name='environment-variables',
                required=(ISiteRoot, IAdminLayer, EnvironmentView),
                provides=IInnerTable)
class EnvironmentVariablesView(InnerTableAdminView, ViewContentProvider):
    """Environment view"""

    table_class = EnvironmentTable
    table_label = _("Environment variables")

    hide_section = True

    weight = 20


#
# Configuration settings
#

class ConfigurationTable(Table):
    """Configuration settings table"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.settings = request.registry.settings

    @reify
    def id(self):
        return '{}_config'.format(super().id)

    @reify
    def values(self):
        return self.settings


@adapter_config(name='setting-name',
                required=(ISiteRoot, IAdminLayer, ConfigurationTable),
                provides=IColumn)
class ConfigurationNameColumn(NameColumn):
    """Setting name column"""

    i18n_header = _("Setting name")
    weight = 10

    def get_value(self, obj):
        """Value getter"""
        return obj


@adapter_config(name='setting-value',
                required=(ISiteRoot, IAdminLayer, ConfigurationTable),
                provides=IColumn)
class ConfigurationValueColumn(NameColumn):
    """Setting value column"""

    i18n_header = _("Value")
    weight = 20

    def get_value(self, obj):
        """Value getter"""
        settings = self.table.values
        return settings.get(obj)


@adapter_config(name='configuration-settings',
                required=(ISiteRoot, IAdminLayer, EnvironmentView),
                provides=IInnerTable)
class ConfigurationView(InnerTableAdminView, ViewContentProvider):
    """Packages versions view"""

    table_class = ConfigurationTable
    table_label = _("Configuration settings")

    hide_section = True

    weight = 30
