# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

class LicenseProvider():

    def name(self):
        return None

    def lookup_license(self, url):
        logging.debug(f'lookup_license_package {url}')
        data = self.lookup_license_impl(url)
        data['provider'] = self.name()
        data['url'] = url
        data['status'] = data['license'] is not None

        return data

    def lookup_license_package(self, orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        logging.debug(f'lookup_license_package {orig_url}, {pkg_type}, {pkg_namespace}, {pkg_name}, {pkg_version}, {pkg_qualifiers}, {pkg_subpath}')
        data = self.lookup_license_package_impl(orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None)
        data['provider'] = self.name()
        data['url'] = orig_url
        data['status'] = data['license'] is not None
        return data

    def parameters_to_url(self, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        raise Exception('Subclasses to LicenseProvider must implment: parameters_to_url')
