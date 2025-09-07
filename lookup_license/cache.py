# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from diskcache import Cache
from datetime import datetime

import logging

class LookupLicenseCache():

    def _init_cache(self, update=False):
        logging.debug('LookupLicenseCache _init_cache')
        self.cache = Cache(f'{Path.home()}/.ll/')
        self.enabled = True
        self.update_mode = update

    def set_update_mode(self, enable_update=True):
        self.update_mode = enable_update

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def add(self, key, value):
        if not self.enabled:
            logging.debug(f'LookupLicenseCache is disabled, will not store {key}')
            return

        logging.debug(f'LookupLicenseCache add {key}')

        if not self.cache.add(key, value):
            if self.update_mode:
                self.cache.set(key, value)
                logging.debug('LookupLicenseCache updated: {key}')
        else:
            logging.debug('LookupLicenseCache added: {key}')
            logging.debug('LookupLicenseCache Objects in cache: {self.cache.size}')

    def get(self, key):
        logging.debug(f'LookupLicenseCache get {key}')
        if not self.enabled:
            raise Exception("LookupLicenseCache is disabled")
        if self.update_mode:
            raise Exception("LookupLicenseCache update mode enabled")

        return self.cache[key]

    def close(self):
        self.cache.close()

    def clear(self):
        self.cache.clear()

    def __new__(cls):
        if not hasattr(cls, 'llcache'):
            logging.debug('Creating LookupLicenseCache object')
            cls.llcache = super(LookupLicenseCache, cls).__new__(cls)
            cls.llcache._init_cache()
        return cls.llcache

    def cache(self):
        return self.cache

    def list_cache(self):
        entries = {}
        for entry_key in self.cache:
            entries[entry_key] = self.cache[entry_key]
        return entries
