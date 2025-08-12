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
        return ret
