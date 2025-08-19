#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from licensedcode import cache # noqa: I900
from cachetools import LFUCache
from cachetools import cached
import logging
import traceback

# from flame.license_db import FossLicenses # noqa: I900
# from flame.license_db import Validation # noqa: I900

import lookup_license.config
from lookup_license.license_db import LicenseDatabase

# from lookup_license.lookupurl import LookupURL # noqa: I900

MAX_CACHE_SIZE = 10000
MIN_SCORE = 80
MIN_LICENSE_LENGTH = 200

MAIN_BRANCHES = ['main', 'master']
LICENSE_FILES = ['LICENSE', 'LICENSE.txt', 'COPYING']

class LicenseCache(LFUCache):

    def popitem(self):
        key, value = super().popitem()
        logging.debug(f'Remove cached license item: {key}')
        return key, value

class LicenseTextReader():

    def __init__(self):
        self.expr_prompt = 'Enter license text and press Control-d.\n>>> '
        self.file_prompt = 'Enter license file name and press enter.\n>>> '
        self.url_prompt = 'Enter license URL name and press enter.\n>>> '
        self.eo_license = 'ENDOFLICENSETEXT'

    def read_license_text(self):
        license_lines = []
        print(self.expr_prompt, end='')
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == self.eo_license:
                break
            license_lines.append(line)

        license_text = '\n'.join(license_lines)
        return license_text

    def read_license_file(self):
        print(self.file_prompt, end='')
        try:
            license_file = input()
            return license_file
        except EOFError:
            pass

    def read_license_url(self):
        print(self.url_prompt, end='')
        try:
            license_url = input()
            return license_url
        except EOFError:
            pass

class LookupLicense():

    def __init__(self):
        self.idx = None
        self.license_reader = None

    def __init_license_index(self):
        if not self.idx:
            logging.debug("Initializing license cache")
            self.idx = cache.get_index()
            logging.debug("Initializing license cache finished")

    def __flame_status(self, res):
        return len(res['ambiguities']) == 0

    def __fix_protocol(self, url):
        if not url.startswith('http'):
            url = f'https://{url}'
        return url

    def _guess_codeberg_license_url(self, url):
        urls = []
        for branch in MAIN_BRANCHES:
            for license_file in LICENSE_FILES:
                urls.append(f'{url}/src/branch/{branch}/{license_file}')
        return urls

    def OBSOLETED___fix_url(self, url):
        if "github" in url:
            url_split = url.split('/')
            org = url_split[3]
            proj = url_split[4]
            rest = "/".join([x for x in url_split[5:] if x != 'blob'])
            new = f'https://raw.githubusercontent.com/{org}/{proj}/{rest}'
            logging.debug(f' fixed license url: {url}  --->   {new}')
            return new
        if "cgit.freedesktop.org" in url:
            url_split = url.split('/')
            proj = url_split[3]
            rest = "/".join([x for x in url_split[4:] if x != 'tree'])
            new = f'https://cgit.freedesktop.org/{proj}/plain/{rest}'
            return new
        if "gitlab/" in url:
            new = url.replace('/-/blob/', '/-/raw/')
            return new
        if "codeberg" in url:
            new = url.replace('/src/', '/raw/')
            return new

#    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def lookup_license_text(self, license_text, minimum_score=lookup_license.config.default_minimum_score):
        # if short license text, it is probably a license name
        # try normalizing with foss-flame
        if len(license_text) < MIN_LICENSE_LENGTH:
            try:
                res = LicenseDatabase.expression_license(license_text)
                return {
                    "identification": "flame",
                    "provided": license_text,
                    "normalized": [res['identified_license']],
                    "ambiguities": len(res['ambiguities']),
                    "status": self.__flame_status(res),
                    "meta": res,
                }
            except Exception as e:
                logging.info(f'Failure: {e}')
                logging.debug(traceback.format_exc)

        # either we have a long license text or foss-flame normalization failed
        # proceed with "our" lookup
        self.__init_license_index()
        ret = self.idx.match(
            query_string=license_text,
            min_score=MIN_SCORE,
            unknown_licenses=False,
        )
        scan_result = [r.to_dict() for r in ret]
        identified_licenses = []
        identified_license_names = set()

        # sort lowest score first, to present the lowest score to the user
        sorted_scan_result = sorted(scan_result, key=lambda x: x['score'], reverse=False)
        for s in sorted_scan_result:
            if s['score'] >= minimum_score:
                license_name = LicenseDatabase.expression_license(s['license_expression'])['identified_license']
                if license_name not in identified_license_names:
                    identified_license_names.add(license_name)
                    identified_licenses.append(
                        {
                            "license": license_name,
                            "score": s['score'],
                        })
        return {
            "identification": "lookup-license",
            "provided": license_text,
            "normalized": identified_licenses,
            "ambiguities": 0,
            "status": True,
        }

    def lookup_license_file(self, license_file):
        self.__init_license_index()
        with open(license_file) as fp:
            content = fp.read()
            return self.lookup_license_text(content)

    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def OBSOLETE_lookup_gitrepo_url_shallow(self, url):
        lookup_url = None
        lookup_url.lookup_license_url(url, "gitrepo")

        branched_suggestions = self.gitrepo.suggest_license_files(url)
        for suggestions in branched_suggestions:
            res = self.__lookup_gitrepo_url(url, suggestions)

            if not res:
                continue

            # if a license has been identified,
            # assume this is the branch to use (details can be found in res)
            if res['identified_licenses']:
                return res

        # if no license found, return None (even if implicit)
        return None

    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def OBSOLETE_lookup_purl_shallow(self, purl):
        lookup_url = None
        res = lookup_url.lookup_license_url(purl, "purl")

        return res

        branched_suggestions = self.purl.suggest_license_files(purl)
        for suggestions in branched_suggestions:
            res = self.__lookup_gitrepo_url(purl, suggestions)

            if not res:
                continue

            # if a license has been identified,
            # assume this is the branch to use (details can be found in res)
            if res['identified_licenses']:
                return res

        # if no license found, return None (even if implicit)
        return None

    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def OBSOLETED_lookup_license_url(self, url, url_type):
        print("REALLY! ... isn't this obsoleted???")
        import sys
        sys.exit(1)
        self.__init_license_index()
        lookup_url = None
        res = lookup_url.lookup_license_url(url, url_type)

        return res

        logging.debug(f'LookupLicense:lookup_license_url {url}')
        fixed_urls = self.__fix_url(url)
        urls = [url, fixed_urls]
        retriever = None

        for _url in urls:
            retrieved_result = retriever.lookup_license_urls(url)
            decoded_content = retrieved_result['decoded_content']
        res = self.lookup_license.lookup_license_text(decoded_content)
        res['provided'] = retrieved_result['provided']
        res['tried_urls'] = retrieved_result['tried_urls']

        return res
