# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookuplicense import LookupLicense
from lookup_license.retrieve import Retriever

import logging

class LookupURL:

    def __init__(self):
        logging.debug("LookupURL()")
        self.lookup_license = LookupLicense()

    def lookup_url(self, url):
        return self.lookup_license_urls(url, [[url]])

    def lookup_license_urls(self, url, suggestions):
        logging.debug(f'lookup_license_urls {suggestions}')
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
                    if licenses_from_url:
                        successful_urls.append({
                            'url': _url,
                            'original_url': _orig_url,
                            'license': licenses_from_url,
                            'lookup-type': 'license-file',
                            'downloaded': retrieved_result,
                            'details': _lic,
                        })
                        license_identifications.extend(licenses_from_url)

            if license_identifications:
                break
        logging.debug(f'lookup_license_url({license} ==> {" AND ".join(license_identifications)}')

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
