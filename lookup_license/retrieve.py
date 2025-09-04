# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.config import http_timeout

import logging
import magic
import requests

class Retriever():

    def _is_text(self, buffer):
        buf_type = magic.from_buffer(buffer).lower()
        text_present = "ascii" in buf_type or "text" in buf_type
        html_present = "html" in buf_type
        return text_present and (not html_present)

    def OBSOLETE__lookup_gitrepo_url(self, url, urls):
        guesses = []
        identified_licenses = set()
        for _url in urls:
            try:
                res = self.lookup_license_url(_url)
            except Exception as e:
                # TODO: handle properly # noqa: T101
                print("eeeeeee " + str(e))

            if res['normalized']:
                for res_object in res['normalized']:
                    lic = res_object['license']
                    identified_licenses.add(lic)
            guesses.append(res)

        return {
            'url': url,
            'identified_licenses': list(identified_licenses),
            'details': guesses,
        }

    def download_url(self, url):
        logging.info(f'download: {url}')
        response = requests.get(url, stream=True, timeout=http_timeout)
        content = response.content
        code = response.status_code
        decoded_content = content.decode('utf-8')
        success = (code != 404)
        res = {
            'decoded_content': decoded_content,
            'provided': url,
            'code': code,
            'success': success,
            'url': url,
        }

        return res
