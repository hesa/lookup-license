# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

# from purltools import purl2clearlydefined  # noqa: I900
from lookup_license.lookupurl.purl2cd import purl2clearlydefined

from lookup_license.lookupurl.license_provider import LicenseProvider
from lookup_license.retrieve import Retriever

import json
import logging

LICENSE_EXPRESSION_PATH = 'licensed.facets.core.discovered.expressions'

class ClearlyDefined(LicenseProvider):

    def name(self):
        return 'https://clearlydefined.io/'

    def purl_to_coordinate(self, purl):
        return purl2clearlydefined(purl)

    def purl_to_coordinate_url(self, purl):
        logging.debug(f'{self.__class__.__name__}:purl_to_coordinate_url {purl}')
        coord = purl2clearlydefined(purl)
        logging.debug(f'{self.__class__.__name__}:purl_to_coordinate_url {purl} => coord: {coord}')
        coord_url = f'https://api.clearlydefined.io/definitions/{coord}'
        logging.debug(f'{self.__class__.__name__}:purl_to_coordinate_url {purl} => coord: {coord} => {coord_url}')
        return coord_url

    def parameters_to_url(self, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        logging.debug(f'{self.__class__.__name__}:parameters_to_url {pkg_type}, {pkg_namespace}, {pkg_name}, {pkg_version}, {pkg_qualifiers}, {pkg_subpath}')
        if pkg_version:
            pkg_version_str = f'/{pkg_version}'
        else:
            pkg_version_str = ''

        if pkg_namespace:
            pkg_namespace_str = f'/{pkg_namespace}'
        else:
            pkg_namespace_str = '/-'

        coordinates = f'{pkg_type}{pkg_namespace_str}/{pkg_name}{pkg_version_str}'
        coord_url = f'https://api.clearlydefined.io/definitions/{coordinates}'
        logging.debug(f'{self.__class__.__name__}:parameters_to_url {pkg_type}, {pkg_namespace}, {pkg_name}, {pkg_version}, {pkg_qualifiers}, {pkg_subpath} => {coord_url}')

        return coord_url

    def lookup_license_package_impl(self, orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        coord_url = self.parameters_to_url(pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers, pkg_subpath)
        return self.lookup_license_impl(coord_url)

    def lookup_license_impl(self, url):
        retriever = Retriever()
        error_msg = None
        if url.startswith('pkg:'):
            # Try url as a purl
            try:
                coord_url = self.purl_to_url(url)
            except Exception:
                logging.debug(f'Could not convert {url} to a coordinate')
                coord_url = None
        else:
            coord_url = url

        if coord_url:
            try:
                retrieved_result = retriever.download_url(coord_url)
                success = retrieved_result['success']
            except Exception:
                success = False
                error_msg = f'Coult not download {coord_url}.'
        else:
            success = False
            error_msg = f'Coult not convert {url} to a coordinate.'

        if not success:
            identified_license = None
        else:
            decoded_content = retrieved_result['decoded_content']
            json_data = json.loads(decoded_content)

            try:
                inner_json = json_data
                for key in LICENSE_EXPRESSION_PATH.split('.'):
                    inner_json = inner_json.get(key)
                inner_json.sort()
                identified_license = ' AND '.join(inner_json)
            except Exception:
                logging.debug(f'Failed getting data from clearlydefined, with "{key}" out of {LICENSE_EXPRESSION_PATH}')
                error_msg = f'Failed getting data from clearlydefined, with "{key}" out of {LICENSE_EXPRESSION_PATH}'
                identified_license = None

        ret = {
            'license': identified_license,
            'data_url': coord_url,
            'data_path': LICENSE_EXPRESSION_PATH,
            'error_message': error_msg,
        }
        return ret
