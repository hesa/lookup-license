#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from licensedcode import cache # noqa: I900
from cachetools import LFUCache
from cachetools import cached
import logging
import magic
import requests
import sys
import traceback

from flame.license_db import FossLicenses # noqa: I900

MAX_CACHE_SIZE = 10000
MIN_SCORE = 80
MIN_LICENSE_LENGTH = 200

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
        logging.debug("Creating LicenseLookup object")
        self.idx = None
        self.fl = FossLicenses()
        self.license_reader = None

    def __init_license_index(self):
        if not self.idx:
            logging.debug("Initializing license cache")
            self.idx = cache.get_index()
            logging.debug("Initializing license cache finished")

    def __flame_status(self, res):
        return len(res['ambiguities']) == 0

    def _is_text(self, buffer):
        return "ascii" in magic.from_buffer(buffer).lower()

    def _fix_url(self, url):
        if "https://github.com" in url:
            url_split = url.split('/')
            org = url_split[3]
            proj = url_split[4]
            rest = "/".join([x for x in url_split[5:] if x != 'blob'])
            new = f'https://raw.githubusercontent.com/{org}/{proj}/{rest}'
            logging.info(f' fixed license url: {url}  --->   {new}')
            return new
        if "https://cgit.freedesktop.org" in url:
            url_split = url.split('/')
            proj = url_split[3]
            rest = "/".join([x for x in url_split[4:] if x != 'tree'])
            new = f'https://cgit.freedesktop.org/{proj}/plain/{rest}'
            return new
        if "https://gitlab.com/" in url:
            new = url.replace('/-/blob/','/-/raw/')
            return new

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
        identified_licenses = [self.fl.expression_license(s['license_expression'])['identified_license'] for s in scan_result]
        return {
            "identification": "lookup-license",
            "provided": license_text,
            "normalized": identified_licenses,
            "ambiguities": 0,
            "meta": scan_result,
        }

    def lookup_license_file(self, license_file):
        self.__init_license_index()
        with open(license_file) as fp:
            content = fp.read()
            return self.lookup_license_text(content)
        
    @cached(cache=LicenseCache(maxsize=MAX_CACHE_SIZE), info=True)
    def lookup_license_url(self, url):
        tried_urls = []
        logging.debug(f'lookup_license_url({url})')
        self.__init_license_index()
        response = requests.get(url, stream=True)
        content = response.content
        code = response.status_code
        decoded_content = content.decode('utf-8')
        tried_urls.append({
            "url": url,
            "status_code": code,
            "content": decoded_content,
        })
        if code == 404 or not self._is_text(decoded_content):
            new_url = self._fix_url(url)
            logging.info(f'Trying {new_url} instead of {url})')
            response = requests.get(new_url, stream=True)
            code = response.status_code
            content = response.content
            decoded_content = content.decode('utf-8')
            tried_urls.append({
                "url": new_url,
                "status_code": code,
                "content": decoded_content,
            })
        if code == 404 or not self._is_text(decoded_content):
            return {
                "identification": "lookup-license",
                "provided": url,
                "normalized": None,
                "ambiguities": 0,
                "meta": {
                    "urls": tried_urls,
                }
            }
        logging.debug(f'looking up content: {decoded_content[:20]}')
        res = self.lookup_license_text(decoded_content)
        res['provided'] = url
        res['tried_urls'] = [x['url'] for x in tried_urls]
        return res

    def _is_text(self, buffer):
        buf_type = magic.from_buffer(buffer).lower()
        text_present = "ascii" in buf_type or "text" in buf_type
        html_present = "html" in buf_type 
        return text_present and (not html_present)
