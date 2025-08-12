from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from packageurl import PackageURL

import logging

class Url(LookupURL):

    def __init__(self):
        logging.debug("Url()")
        self.gitrepo = GitRepo()
        super().__init__()

    def lookup_url(self, url):
        #self.gitrepo = GitRepo()

        # in case it is a url to an HTML page
        urls = {
            'license_raw_url': self.gitrepo.raw_content_url(url),
            'original_url': url
        }
        
        ret = self.lookup_license_urls(url, [[urls]])
        import sys, json
        #print("ret: " + json.dumps(ret, indent=4))
        #sys.exit(1)
        return ret 
