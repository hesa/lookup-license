# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.gem import Gem
from lookup_license.lookupurl.purl import Purl
from lookup_license.lookupurl.purl import Ecosystem
from lookup_license.lookupurl.url import Url
from lookup_license.lookupurl.pypi import Pypi
from lookup_license.lookupurl.swift import Swift

import logging

def _contains(url, strings):
    res = any(map(url.__contains__, strings))
    return res

class LookupURLFactory:

    @staticmethod
    def lookupurl(url_type):
        logging.debug(f'LookupURLFactory:lookup "{url_type}"')
        _lookup_map = {
            'purl': Purl,
            Ecosystem.PYPI.value: Pypi,
            Ecosystem.PYPI: Pypi,
            Ecosystem.GITREPO.value: GitRepo,
            Ecosystem.GITREPO: GitRepo,
            'url': Url,
            Ecosystem.SWIFT.value: Swift,
            Ecosystem.SWIFT: Swift,
            Ecosystem.GEM: Gem,
            Ecosystem.GEM.value: Gem,
        }
        try:
            lookup_class = _lookup_map[url_type]
            lookup_object = lookup_class()
            return lookup_object
        except Exception as e:
            raise Exception(f'Ecosystem "{url_type}" not supported. Exception {e}')

    @staticmethod
    def lookupurl_url(url):
        if not url.startswith('pkg:'):
            raise Exception(f'Purl "{url}" not a valid purl.')
        url_type = None
        if _contains(url, ['gem', 'rubygems']):
            url_type = Ecosystem.GEM
        elif _contains(url, ['pypi']):
            url_type = Ecosystem.PYPI
        elif _contains(url, ['swift']):
            url_type = Ecosystem.SWIFT

        if not url_type:
            raise Exception(f'Purl "{url}" not supported.')

        return LookupURLFactory.lookupurl(url_type)
