# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.license_providers import LicenseProviders
from lookup_license.utils import get_keypath

from lookup_license.retrieve import Retriever

from packageurl import PackageURL  # noqa: I900

import json
import logging
import re

class Pypi(LookupURL):

    def __init__(self):
        logging.debug("Pypi()")
        self.gitrepo = GitRepo()
        super().__init__()

    def _try_pypi_package_url(self, pypi_url):
        retriever = Retriever()
        retrieved_result = retriever.download_url(pypi_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        json_data = json.loads(decoded_content)

        #
        # Handle classifiers (in pypi JSON data)
        #
        licenses_from_package = []
        for classifier in json_data['info']['classifiers']:
            if 'license' in classifier.lower():
                license_object = {
                    'url': pypi_url,
                    'section': 'info.classifiers',
                    'license': classifier,
                }
                licenses_from_package.append(license_object)

        #
        # Handle license variable (in pypi JSON data)
        #
        license_var = json_data['info'].get('license', None)
        if license_var:
            license_object = {
                'url': pypi_url,
                'section': 'info.license',
                'license': license_var,
            }
            licenses_from_package.append(license_object)
        #
        # Identify source code repository
        #
        repo_suggestions = []
        JSON_PATHS = [
            'info.project_urls.Source',
            'info.project_urls.Source Code',
            'info.project_urls.Code',
            'info.project_url',
            'info.homepage',
            'info.project_urls.Homepage',
        ]
        # TODO: add version from JSON data to suggested URL # noqa: T101
        for complete_path in JSON_PATHS:
            inner_json_data = json_data
            for path in complete_path.split('.'):
                if path in inner_json_data:
                    inner_json_data = inner_json_data[path]
                else:
                    inner_json_data = None
                    break
            if inner_json_data:
                repo_suggestions.append({
                    'repository': inner_json_data,
                    'package_url': pypi_url,
                    'package_path': complete_path,
                })
        repo_url = self._get_pypi_repo(json_data, JSON_PATHS)
        if not repo_url:
            repo_url = ''

        homepage = get_keypath(json_data, 'info.home_page')
        name = get_keypath(json_data, 'info.name')
        version = get_keypath(json_data, 'info.version')

        package_details = {
            'package_url': pypi_url,
            'package_type': self.name(),
            'homepage': homepage,
            'name': name,
            'version': version,
            'repository': repo_url,
        }

        return {
            'licenses': licenses_from_package,
            'repo_suggestions': repo_suggestions,
            'package_details': package_details,
        }

    def OBSOLETE_get_key(self, path, data):
        inner_data = data
        for sub_path in path.split('.'):
            if sub_path in inner_data:
                inner_data = inner_data[sub_path]
            else:
                return None
        return inner_data

    def _get_pypi_repo(self, paths, data):
        for path in paths:
            _data = get_keypath(data, path)
            if _data:
                return _data

    def _get_parameters(self, url, version):
        if 'https://pypi.org/project/' in url:
            stripped_url = url.strip('/')
            stripped_url = re.sub(r'/json[/]*$', '', stripped_url)
            stripped_url = re.sub(r'^http[s]*://pypi.org/project/', '', stripped_url)
            splits = stripped_url.split('/')
            pkg_name = splits[0]
            pkg_version = splits[1]
        elif 'https://pypi.org/pypi/' in url:
            stripped_url = url.strip('/')
            stripped_url = re.sub(r'/json[/]*$', '', stripped_url)
            stripped_url = re.sub(r'^http[s]*://pypi.org/pypi/', '', stripped_url)
            splits = stripped_url.split('/')
            pkg_name = splits[0]
            pkg_version = splits[1]
        elif 'https://pypi.org/' in url:
            raise Exception(f'pypi URLs should start with https://pypi.org/project/ or https://pypi.org/pypi/. The following URL is incorrect: {url}')
            # Create ClearlyDefined coordinate from pypi path
            stripped_url = re.sub(r'/json[/]*$', '', url)
            stripped_url = re.sub(r'^http[s]*://pypi.org/pypi/', '', stripped_url)
            splits = stripped_url.split('/')
            pkg_name = splits[0]
            pkg_version = splits[1]
        elif url.startswith('pkg:'):
            purl_dict = PackageURL.from_string(url).to_dict()
            pkg_name = purl_dict['name']
            pkg_version = purl_dict['version']
        else:
            # Create parameters from pypi package name
            stripped_url = re.sub(r'^[/]*pypi/', '', url)
            splits = stripped_url.split('@')
            pkg_name = splits[0]
            try:
                pkg_version = splits[1]
            except Exception:
                pkg_version = version

        return {
            'name': pkg_name,
            'version': pkg_version,
        }

    def lookup_package(self, url):
        logging.debug(f'{self.__class__.__name__}:lookup_package {url}')

        url = url.strip('/')

        if url.startswith('pkg:'):
            # purl
            purl_object = PackageURL.from_string(url)
            pypi_urls = []
            if purl_object.version:
                pypi_urls.append(f'https://pypi.org/pypi/{purl_object.name}/{purl_object.version}/json')
            else:
                pypi_urls.append(f'https://pypi.org/pypi/{purl_object.name}/json')
        elif url.startswith('http'):
            pypi_urls = [
                f'{url}/json',
                f'{url}/json'.replace('/project/', '/pypi/'),
                url,
            ]
        else:
            if '/' in url:
                raise Exception('A python package cannot contain "/".')
            new_url = url.replace('@', '/')
            new_url = new_url.replace('==', '/')
            pypi_urls = [
                f'https://pypi.org/pypi/{new_url}/json',
            ]

        #
        # Loop through pypi urls, if data found in one url
        # scrape the configuration data and the repos suggested
        identified_pypi_data = None
        for pypi_url in pypi_urls:
            try:
                pypi_data = self._try_pypi_package_url(pypi_url)
                if pypi_data:
                    # this pypi url had data
                    # use the data below
                    identified_pypi_data = pypi_data
                    break
            except Exception:
                logging.debug(f'Ignoring pypi url: {pypi_url}')

        return identified_pypi_data

    def lookup_providers(self, url, version=None):
        logging.debug(f'{self.__class__.__name__}:lookup_providers {url}, {version}')

        parameters = self._get_parameters(url, version)
        logging.debug(f'{self.__class__.__name__}:lookup_providers parameters: {parameters}')

        # Identify licenses at providers
        providers = LicenseProviders().lookup_license_package(url, 'pypi', 'pypi', parameters['name'], parameters['version'])
        logging.debug(f'{self.__class__.__name__}:lookup_providers_impl providers: {providers}')

        return providers

    def name(self):
        logging.debug(f'{self.__class__.__name__}:name()')
        return 'Pypi'

    def lookup_url_impl(self, url, package_data=None, providers_data=None):
        logging.debug(f'{self.__class__.__name__}:lookup_url_impl {url}, {package_data is not None}, {providers_data is not None}')
        repo_data = None

        if not package_data:
            return None

        #
        # The data above contains suggestions for repository
        # urls. Loop through these and analyse them if data is found,
        # use the data from that repo
        uniq_repos = set([repo['repository'] for repo in package_data['repo_suggestions']]) # noqa: C403
        repo_data = None
        for repo in uniq_repos:
            repo_data = self.gitrepo.lookup_url(repo)
            success = repo_data['url_data']['success']
            if success:
                break
            else:
                repo_data = None

        return repo_data
