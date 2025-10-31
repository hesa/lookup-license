# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.license_providers import LicenseProviders

from lookup_license.retrieve import Retriever

from packageurl import PackageURL # noqa: I900

import html
import logging

class Go(LookupURL):

    def __init__(self):
        logging.debug("Go()")
        self.gitrepo = GitRepo()
        super().__init__()

    def homepage_repo_url(self, lines):
        repo = False
        repo_url = None
        for encoded_line in lines:
            if '>Repository<' in encoded_line:
                repo = True
            if repo:
                if '<a href' in encoded_line:
                    href = encoded_line.split()[1]
                    url = href.split('=')[1].replace('"', '')
                    repo = False
                    repo_url = url
        return repo_url

    def homepage_license_texts(self, homepage_lines):
        license_texts = []
        license_text = []
        inside_license_text = False
        for line in homepage_lines:
            encoded_line = line
            if inside_license_text:
                if '</pre>' in encoded_line:
                    inside_license_text = False
                    license_texts.append('\n'.join(license_text))
                    license_text = []
                else:
                    license_text.append(encoded_line)
            elif '<pre class="License-contents">' in encoded_line:
                inside_license_text = True
                license_text.append(encoded_line.replace('<pre class="License-contents">', ''))
        return license_texts

    def homepage_license_files(self, lines):
        license_files = []
        for encoded_line in lines:
            if '>Source: ' in encoded_line:
                lic_1 = encoded_line.split('>')[1]
                lic_2 = lic_1.split('<')[0]
                lic_file = lic_2.replace('Source: ', '')
                license_files.append(lic_file)
        return license_files

    def get_parameters_pkg_go_dev(self, url, version):
        logging.debug(f'{self.__class__.__name__}:get_parameters_pkg_go_dev {url}, {version}')
        stripped_url = url.replace('https://pkg.go.dev/', '')
        splits = stripped_url.split('/')
        repo_host = splits[0]
        repo_org = splits[1]
        name_splits = splits[1].split('@')
        pkg_name = name_splits[0]
        if len(name_splits) > 1:
            pkg_version = name_splits[1]
        else:
            pkg_version = None
        ret = {
            'name': pkg_name,
            'namespace': f'go/golang/{repo_host}/{repo_org}',
            'version': pkg_version,
        }
        return ret

    def get_parameters_pkg_only(self, url, version):
        logging.debug(f'{self.__class__.__name__}:get_parameters_pkg_only {url}, {version}')

        if "/" not in url:
            logging.debug('A go package must have a "/" to identify it correctly')
            return None

        stripped_url = url.replace('https://pkg.go.dev/', '')
        splits = stripped_url.split('/')
        repo_host = splits[0]
        repo_org = splits[1]
        name_splits = splits[1].split('@')
        pkg_name = name_splits[0]
        if len(name_splits) > 1:
            pkg_version = name_splits[1]
        else:
            pkg_version = None

        ret = {
            'name': pkg_name,
            'namespace': f'go/golang/{repo_host}/{repo_org}',
            'version': pkg_version,
        }
        return ret

    def get_parameters(self, url, version):
        logging.debug(f'{self.__class__.__name__}:get_parameters {url}, {version}')
        if url.startswith('https://pkg.go.dev'):
            return self.get_parameters_pkg_go_dev(url, version)
        else:
            return self.get_parameters_pkg_only(url, version)
        return {'name': 'go'}

    def lookup_package(self, url):
        logging.debug(f'{self.__class__.__name__}:lookup_package {url}')

        url = url.strip('/')

        if url.startswith('pkg:'):
            # purl
            purl_object = PackageURL.from_string(url)
            go_urls = []
            if purl_object.version:
                go_urls.append(f'https://pkg.go.dev/{purl_object.name}/{purl_object.version}/json')
            else:
                go_urls.append(f'https://pkg.go.dev//{purl_object.name}/json')
        elif url.startswith('http'):
            # https
            go_urls = [
                url,
                f'{url}/json',
                f'{url}/json'.replace('/project/', '/go/'),
            ]
        else:
            go_urls = [
                f'https://pkg.go.dev/{url}',
            ]

        #
        # Loop through go urls, if data found in one url
        # scrape the configuration data and the repos suggested
        identified_go_data = None
        for go_url in go_urls:
            go_data = self._try_go_package_page(go_url)
            if go_data:
                # this go url had data
                # use the data below
                identified_go_data = go_data
                break
        return identified_go_data

    def homepage_lines(self, retriever, go_url):
        retrieved_result = retriever.download_url_raw(go_url)
        lines = []
        for line in retrieved_result.iter_lines():
            encoded_line = line.decode(encoding="utf-8")
            plain_line = html.unescape(encoded_line)
            lines.append(plain_line)
        return lines

    def _try_go_package_page(self, go_url):

        retriever = Retriever()
        repo_url_content_lines = self.homepage_lines(retriever, go_url)
        repo_url_license_lines = self.homepage_lines(retriever, f'{go_url}?tab=licenses')

        repo_url = self.homepage_repo_url(repo_url_content_lines)

        license_texts = self.homepage_license_texts(repo_url_license_lines)

        # TODO: should we pass on the license files? # noqa: T101
        # license_files = self.homepage_license_files(repo_url_license_lines) # noqa: F128

        repo_suggestions = [{
            'repository': repo_url,
            'config_url': go_url,
            'config_path': '',
        }]

        package_details = {
            'package_url': go_url,
            'package_type': self.name(),
            'package_license_texts': license_texts,
            'homepage': '',
            'name': '',
            'version': '',
            'repository': repo_url,
        }

        return {
            'licenses': [],
            'repo_suggestions': repo_suggestions,
            'package_details': package_details,
        }

    def name(self):
        logging.debug(f'{self.__class__.__name__}:name()')
        return 'Go'

    def _get_key(self, path, data):
        inner_data = data
        for sub_path in path.split('.'):
            if sub_path in inner_data:
                inner_data = inner_data[sub_path]
            else:
                return None
        return inner_data

    def _get_go_repo(self, paths, data):
        for path in paths:
            _data = self._get_key(path, data)
            if _data:
                return _data

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
            if not repo:
                continue
            repo_data = self.gitrepo.lookup_url(repo)
            success = repo_data['url_data']['success']
            if success:
                break
            else:

                repo_data = None
        return repo_data

    def lookup_providers(self, url, version=None):
        logging.debug(f'{self.__class__.__name__}:lookup_providers {url}, {version}')

        parameters = self.get_parameters(url, version)
        logging.debug(f'{self.__class__.__name__}:lookup_providers parameters: {parameters}')

        # Identify licenses at providers
        providers = LicenseProviders().lookup_license_package(url, 'go', None, parameters['name'], parameters['version'])
        logging.debug(f'{self.__class__.__name__}:lookup_providers_impl providers: {providers}')

        return providers
