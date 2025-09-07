# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.clearlydefined import ClearlyDefined
from lookup_license.lookupurl.purldb import PurlDB

import logging

class LicenseProviders:

    def __init__(self):
        self.provider_list = [
            ClearlyDefined(),
            PurlDB(),
        ]
        self.name_namespace_map = {
            'pypi': 'pypi',
            'gem': 'rubygems',
            'gem/rubygems': None,
        }

    def providers(self):
        return [x.name() for x in self.provider_list]

    def lookup_license_package(self, orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        logging.debug(f'{self.__class__.__name__}:lookup_license_package {orig_url}, {pkg_type}, {pkg_namespace}, {pkg_name}, {pkg_version}, {pkg_qualifiers}, {pkg_subpath}')
        providers = {}

        if not pkg_namespace or pkg_namespace == '':
            pkg_namespace = self.name_namespace_map[pkg_type]

        for provider in self.provider_list:
            name = provider.name()
            provider_data = provider.lookup_license_package(orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers, pkg_subpath)
            providers[name] = provider_data

        return providers
