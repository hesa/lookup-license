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

MAX_CACHE_SIZE = 10000

class LicenseCache(LFUCache):

    def popitem(self):
        key, value = super().popitem()
        logging.debug(f'Remove cached license item: {key}')
        return key, value

class LookupLicense():

    def __init__(self):
        logging.debug("Creating LicenseLookup object")
        self.idx = None

    def __init_license_index(self):
        if not self.idx:
            logging.debug("Initializing license cache")
            self.idx = cache.get_index()
            logging.debug("Initializing license cache finished")
            
    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def lookup_license_text(self, license_text):
        self.__init_license_index()
        ret = self.idx.match(
            query_string=license_text,
            min_score=0,
            unknown_licenses=False,
        )
        return [r.to_dict() for r in ret]
    
    def lookup_license_file(self, license_file):
        self.__init_license_index()
        with open(license_file) as fp:
            content = fp.read()
            return self.lookup_license_text(content)
    
