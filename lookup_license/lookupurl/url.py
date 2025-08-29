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

    def lookup_url_impl(self, url, package_data=None, providers_data=None):
        urls = {
            'license_raw_url': self.gitrepo.raw_content_url(url),
            'original_url': url,
        }

        ret = self.lookup_license_urls(url, [[urls]])

        return ret
