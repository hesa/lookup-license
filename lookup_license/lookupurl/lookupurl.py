# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookuplicense import LookupLicense
from lookup_license.retrieve import Retriever
from lookup_license.cache import LookupLicenseCache
from lookup_license.license_db import LicenseDatabase

from license_expression import ExpressionError

import logging

class LookupURL:

    def __init__(self):
        logging.debug("LookupURL()")
        self.lookup_license = LookupLicense()

    def lookup_package(self, url):
        logging.debug(f'{self.__class__.__name__}:lookup_package {url}')
        return None

    def lookup_providers(self, url, version):
        logging.debug(f'{self.__class__.__name__}:lookup_providers {url}, {version}')
        return None

    def name(self):
        logging.debug(f'{self.__class__.__name__}:lookup_name()')
        return 'LookupURL'

    def lookup_url(self, url):
        logging.debug(f'{self.__class__.__name__}:lookup_url {url}')

        try:
            return LookupLicenseCache().get(url)
        except Exception as e:
            logging.debug(f'lookup_url: failed to get data from cache for {url}, {e}')

        # Lookup package data (e.g. from pypi.org), if any
        # .. this is typically implemented by sub classes

        package_data = self.lookup_package(url)
        if package_data:
            try:
                version = package_data.get('package_details').get('version')
            except Exception:
                version = None
        else:
            version = None

        # Identify licenses at providers
        # .. this is typically implemented by sub classes
        providers_data = self.lookup_providers(url, version)

        # Identify licenses from urls (e.g. from package_data)
        # .. this is typically implemented by sub classes
        url_data = self.lookup_url_impl(url, package_data, providers_data)

        licenses_object = self.licenses(package_data, url_data, providers_data)

        #
        # pack data
        #
        data = {
            'provided': url,
            'provided_type': self.name(),
            'package_data': package_data,
            'providers_data': providers_data,
            'url_data': url_data,
            'package_licenses': licenses_object['package_license'],
            'identified_license': licenses_object['identified_license'],
            'identified_license_string': licenses_object['identified_license_string'],
        }

        logging.debug(f'add to cache: {url}')
        LookupLicenseCache().add(url, data)

        return data

    def lookup_url_impl(self, url):
        return self.lookup_license_urls(url, [[url]])

    def lookup_license_urls(self, url, suggestions):
        logging.debug(f'{self.__class__.__name__}:lookup_license_urls {url}, {suggestions is not None}')
        retriever = Retriever()

        failed_urls = []
        successful_urls = []
        license_identifications = []

        for suggestion_list in suggestions:
            for url_object in suggestion_list:
                _url = url_object['license_raw_url']
                _orig_url = url_object['original_url']

                # download
                retrieved_result = retriever.download_url(_url)
                success = retrieved_result['success']

                if not success:
                    failed_urls.append({
                        'url': _url,
                        'original_url': _orig_url,
                        'failed': 'download',
                        'failure_details': retrieved_result,
                    })
                    continue

                # identify license
                decoded_content = retrieved_result['decoded_content']
                lic = self.lookup_license.lookup_license_text(decoded_content)
                status = lic["status"]
                if not status:
                    failed_urls.append({
                        'url': _url,
                        'original_url': _orig_url,
                        'downloaded': retrieved_result,
                        'failed': 'lookup-license',
                        'failure_details': lic,
                    })
                    continue

                licenses_from_url = []
                if status:
                    for _lic in lic['normalized']:
                        licenses_from_url.append(_lic["license"])
                    licenses_from_url_str = ' AND '.join(licenses_from_url)
                    if licenses_from_url:
                        successful_urls.append({
                            'url': _url,
                            'original_url': _orig_url,
                            'license': licenses_from_url_str,
                            'lookup-type': 'license-file',
                            'downloaded': retrieved_result,
                            'details': _lic,
                        })
                        license_identifications.extend(licenses_from_url)

            if license_identifications:
                break
        logging.debug(f'lookup_license_url ({license} ==> {" AND ".join(license_identifications)}')

        if license_identifications:
            identified_license = license_identifications
            success = True
        else:
            identified_license = None
            success = False

        res = {
            'provided': url,
            'details': {
                'suggestions': suggestions,
                'failed_urls': failed_urls,
                'successful_urls': successful_urls,
            },
            'identified_license': identified_license,
            'success': success,
        }
        return res

    def licenses(self, config_data, repo_data, providers_data):
        all_licenses = set()

        if config_data:
            licenses_from_config = config_data['licenses']
        else:
            licenses_from_config = []

        if licenses_from_config:
            for lic in licenses_from_config:
                all_licenses.add(lic['license'])

        if repo_data and repo_data['identified_license']:
            for lic in repo_data['identified_license']:
                all_licenses.add(lic)
            repo_licenses = repo_data['identified_license']
        else:
            repo_licenses = []

        providers_licenses = []
        if providers_data:
            for provider in providers_data:
                lic = providers_data[provider]['license']
                if lic:
                    all_licenses.add(lic)
                    providers_licenses.append(lic)

        try:
            identified_license = [LicenseDatabase.expression_license_identified(x) for x in all_licenses]
        except ExpressionError:
            identified_license = all_licenses

        try:
            identified_license_string = LicenseDatabase.summarize_license(all_licenses)
        except ExpressionError:
            identified_license_string = ', '.join(all_licenses)

        ret = {
            'package_license': licenses_from_config,
            'repo_license': repo_licenses,
            'providers_license': providers_licenses,
            'all': list(all_licenses),
            'identified_license': identified_license,
            'identified_license_string': identified_license_string,
        }
        return ret
