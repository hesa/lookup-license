# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL

from packageurl import PackageURL  # noqa: I900
from packageurl.contrib import purl2url  # noqa: I900

from lookup_license.lookupurl.gem import Gem
from lookup_license.lookupurl.pypi import Pypi
from lookup_license.lookupurl.swift import Swift
from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.maven import Maven

from enum import Enum
import logging

class Ecosystem(Enum):
    PYPI = 'pypi'
    GITREPO = 'git'
    SWIFT = 'swift'
    GEM = 'gem'
    MAVEN = 'maven'


class Purl(LookupURL):

    def __init__(self):
        logging.debug("Purl()")
        self.gitrepo = GitRepo()

        super().__init__()

    def _purl_handler(self, purl):
        purl_object = PackageURL.from_string(purl)
        _purl_handlers = {
            'swift': Swift,
            'pypi': Pypi,
            'github': GitRepo,
            'gem': Gem,
            'maven': Maven,
        }
        return _purl_handlers[purl_object.type]()

    def _github_repo_url(self, purl):
        """
        Return a github repo URL from the `purl` string.
        """
        purl_data = PackageURL.from_string(purl)
        purl_namespace = purl_data.namespace
        name = purl_data.name
        version = purl_data.version
        qualifiers = purl_data.qualifiers

        if not name:
            return

        if not purl_namespace:
            logging.debug("NAME SPACE MISSING")

        if purl_data.type == 'swift':
            repo_url = f"https://{purl_namespace}/{name}"
        else:
            repo_url = f"https://github.com/{purl_namespace}/{name}"

        if version:
            url_parts = repo_url.split('/')
            version_prefix = qualifiers.get('version_prefix', '')
            repo_url = f'{"/".join(url_parts[:5])}/tree/{version_prefix}{version}'

        return repo_url

    def _guess_repo_url(self, purl):
        purl_object = PackageURL.from_string(purl)
        purl_name = purl_object.name

        if purl_object.type == 'github' or (purl_object.namespace and 'github' in purl_object.namespace):
            return self._github_repo_url(purl)
        elif purl_object.type == 'pypi':
            pypi_data = Pypi().lookup_url(purl)

            if pypi_data:
                return pypi_data

        else:
            # try using purl2url
            repo_url = purl2url.get_repo_url(purl)
            if not repo_url:
                raise Exception(f'Could not get repo url for {purl}')
            import sys
            sys.exit(1)
        return f'github.com/{purl_object.namespace.replace("github.com/", "")}/{purl_name}'

    def repo_url(self, purl):
        return self._guess_repo_url(purl)

    def suggest_urls(self, purl):
        repo_url = self.repo_url(purl)

        if repo_url:
            return self.gitrepo.suggest_license_files(repo_url)

        return None

    def lookup_url_impl(self, url, package_data, providers_data):
        logging.debug(f'{self.__class__.__name__}:lookup_url_impl {url}, {package_data is not None}, {providers_data is not None} ')

        purl_handler = self._purl_handler(url)
        logging.debug(f'Purl: lookup_url: {purl_handler}')

        data = purl_handler.lookup_url(url)
        logging.debug(f'Purl: lookup_url: {purl_handler}  finished work')

        logging.debug('Purl: data retrieved and will be returned')
        return data
