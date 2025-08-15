# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

import logging

class Url(LookupURL):

    def __init__(self):
        logging.debug("Url()")
        self.gitrepo = GitRepo()
        super().__init__()

    def lookup_url(self, url):
        urls = {
            'license_raw_url': self.gitrepo.raw_content_url(url),
            'original_url': url,
        }

        ret = self.lookup_license_urls(url, [[urls]])

        licenses_object = self.gitrepo.licenses([], ret)
        repositories = []

        ret['provided'] = url
        ret['meta'] = {}
        ret['meta']['url_type'] = 'url'
        ret['meta']['config_details'] = []
        ret['meta']['repository'] = ', '.join(repositories)
        ret['details']['config_licenses'] = licenses_object['config_license']
        ret['identified_license'] = licenses_object['identified_license']
        ret['identified_license_string'] = licenses_object['identified_license_string']

        return ret
