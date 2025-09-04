# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.license_provider import LicenseProvider
from lookup_license.retrieve import Retriever

import json
import logging

class PurlDB(LicenseProvider):

    def name(self):
        return 'https://public.purldb.io'

    def parameters_to_url(self, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        purl = f'pkg:{pkg_type}/{pkg_namespace}/{pkg_name}@{pkg_version}'
        purldb_url = f'https://public.purldb.io/api/collect/?purl={purl}'
        return purldb_url

    def lookup_license_package_impl(self, orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        purldb_url = self.parameters_to_url(pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers, pkg_subpath)
        return self.lookup_license_impl(purldb_url)

    def lookup_license_impl(self, url):
        retriever = Retriever()
        error_msg = None
        if url.startswith('pkg:'):
            # Try url as a purl
            try:
                purldb_url = self.purl_to_url(url)
            except Exception:
                logging.debug(f'Could not convert {url} to a purldb url')
                purldb_url = None
        else:
            purldb_url = url

        if purldb_url:
            try:
                retrieved_result = retriever.download_url(purldb_url)
                success = retrieved_result['success']
            except Exception as e:
                success = False
                error_msg = f'Coult not download {purldb_url}. Exception: {e}.'
        else:
            success = False
            error_msg = f'Coult not convert {url} to a purldb url.'

        if not success:
            identified_license = None
        else:
            decoded_content = retrieved_result['decoded_content']
            json_data = json.loads(decoded_content)

            try:
                licenses = []
                for lic_det in json_data[0]['license_detections']:
                    licenses.append(lic_det['license_expression_spdx'])
                licenses.sort()
                identified_license = ' AND '.join(licenses)
            except Exception:
                error_msg = 'Failed getting data from purldb'
                logging.debug(error_msg)
                identified_license = None

        ret = {
            'license': identified_license,
            'data_url': purldb_url,
            'data_path': '[0].["license_detections"]["license_expression_spdx"]',
            'error_message': error_msg,
        }
        return ret
