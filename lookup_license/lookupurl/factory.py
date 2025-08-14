# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.gem import Gem
from lookup_license.lookupurl.purl import Purl
from lookup_license.lookupurl.url import Url
from lookup_license.lookupurl.pypi import Pypi
from lookup_license.lookupurl.swift import Swift

def _contains(url, strings):
    res = any(map(url.__contains__, strings))
    return res

class LookupURLFactory:

    @staticmethod
    def lookupurl(url_type):
        _lookup_map = {
            'purl': Purl,
            'pypi': Pypi,
            'gitrepo': GitRepo,
            'url': Url,
            'swift': Swift,
            'gem': Gem,
        }
        lookup_obj = _lookup_map[url_type]()

        return lookup_obj
