#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from licensedcode import cache
from cachetools import LFUCache
from cachetools import cached
import logging
import sys
import time

from flame.license_db import FossLicenses

MAX_CACHE_SIZE = 10000
MIN_SCORE=80
MIN_LICENSE_LENGTH=200

class LicenseCache(LFUCache):

    def popitem(self):
        key, value = super().popitem()
        logging.debug(f'Remove cached license item: {key}')
        return key, value

class LookupLicense():

    def __init__(self):
        logging.debug("Creating LicenseLookup object")
        self.idx = None
        self.fl = FossLicenses()

    def __init_license_index(self):
        if not self.idx:
            logging.debug("Initializing license cache")
            self.idx = cache.get_index()
            logging.debug("Initializing license cache finished")

    def __flame_status(self, res):
        return len(res['ambiguities']) == 0

    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def lookup_license_text(self, license_text):
        # if short license text, it is probably a license name
        # try normalizing with foss-flame 
        if len(license_text) < MIN_LICENSE_LENGTH:
            try:
                res = self.fl.expression_license(license_text)
                return {
                    "identification": "flame",
                    "provided": license_text,
                    "normalized": [ res['identified_license'] ],
                    "ambiguities": len(res['ambiguities']),
                    "status": self.__flame_status(res),
                    "meta": res
                }
            except:
                pass

        # either we have a long license text or foss-flame normalization failed
        # proceed with "our" lookup
        self.__init_license_index()
        ret = self.idx.match(
            query_string=license_text,
            min_score=MIN_SCORE,
            unknown_licenses=False,
        )
        #print("r" + str(ret))
        scan_result = [r.to_dict() for r in ret]
        #print("r" + str(scan_result))
        identified_licenses = [ self.fl.expression_license(s['license_expression'])['identified_license'] for s in scan_result]
        return {
            "identification": "lookup-license",
            "provided": license_text,
            "normalized": identified_licenses,
            "ambiguities": 0,
            "meta": scan_result
        }
    
    def lookup_license_file(self, license_file):
        self.__init_license_index()
        with open(license_file) as fp:
            content = fp.read()
            return self.lookup_license_text(content)
    
