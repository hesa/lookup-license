# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.license_providers import LicenseProviders
from lookup_license.utils import contains
from lookup_license.utils import get_keypath

from lookup_license.retrieve import Retriever

from packageurl import PackageURL  # noqa: I900

import xmltodict
import logging

class Maven(LookupURL):

    def __init__(self):
        logging.debug("Pypi()")
        self.gitrepo = GitRepo()
        self.valid_namespaces = ['mavencentral', 'mavengoogle', 'gradleplugin']
        self.google_terms = ['androidx', 'com.android', 'mavengoogle']

        super().__init__()

    def _is_google(self, url):
        return contains(url, self.google_terms)

    def _valid_namespace(self, ns):
        return contains(ns, self.valid_namespaces)

    def _pkg_to_pom_url(self, url):
        purl_object = PackageURL.from_string(url)
        ns = purl_object.namespace
        n = purl_object.name
        v = purl_object.version

        if not self._valid_namespace(ns):
            logging.warning(f'Maven PURL "{url}" and the namespace "{ns}" does not contain any of the following namespaces {self.valid_namespaces} and is perhaps not valid.')

        # Figure out POM url
        if self._is_google(url):
            ns = purl_object.namespace.replace('.', '/')
            pom_url = f'https://maven.google.com/{ns}/{n}/{v}/{n}-{v}.pom'
        else:
            if 'mavencentral' in ns:
                ns = purl_object.namespace.replace('.', '/').replace('mavencentral/', '')
                pom_url = f'https://repo1.maven.org/maven2/{ns}/{n}/{v}/{n}-{v}.pom'
            else:
                logging.warning(f'Maven PURL "{url}" and the namespace "{ns}" is currently not supported. File a bug')
                pom_url = None
        return pom_url

    def _http_to_pkg(self, url):
        if self._is_google(url):
            logging.debug("GOOGLE not supported as we speak")
            pass
        else:
            if 'mvnrepository.com' in url:
                new_url = url.strip('/').replace('https://mvnrepository.com/artifact/', '')

                splits = new_url.split('/')
                names = '/'.join(splits[:-1])
                version = splits[-1]

                pkg_url = f'pkg:maven/mavencentral/{names}@{version}'
                return pkg_url

        raise Exception('Converting {url} to Purl is not supported. Currently only urls with "mvnrepository.com" and non-Google related are supported.')

    def _url_to_pom_url(self, url):
        pom_url = None
        if url.startswith('pkg:'):
            pom_url = self._pkg_to_pom_url(url)
        elif url.startswith('https://'):
            purl = self._http_to_pkg(url)
            pom_url = self._pkg_to_pom_url(purl)
        return pom_url

    def _suggest_repo_from_pom(self, url, data):
        try:
            project_data = data['project']
        except Exception:
            project_data = data

        repo_suggestions = []
        POM_REPO_PATHS = ['scm.url']
        for repo_path in POM_REPO_PATHS:
            repo = get_keypath(project_data, 'scm.url')
            if repo:
                repo_suggestions.append({
                    'repository': repo,
                    'package_url': url,
                    'package_path': repo_path,
                })

        return repo_suggestions

    def lookup_package(self, url):
        pom_url = self._url_to_pom_url(url)

        if not pom_url:
            return None

        # Read POM file
        retriever = Retriever()
        retrieved_result = retriever.download_url(pom_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        data_dict = xmltodict.parse(decoded_content)

        licenses_from_package = []
        try:
            dict_project = data_dict['project']
        except Exception:
            dict_project = data_dict

        repo_suggestions = self._suggest_repo_from_pom(pom_url, data_dict)

        # licenses
        try:
            dict_licenses = dict_project['licenses']
            for lic in dict_licenses.values():

                license_object = {
                    'url': pom_url,
                    'section': 'project.licenses',
                    'license': lic['name'],
                }
                licenses_from_package.append(license_object)
        except Exception:
            logging.debug(f'Could not find license in {pom_url}.')

        package_details = {
            'package_url': pom_url,
            'package_type': self.name(),
            'homepage': 'homepage',
            'name': dict_project.get('name', ''),
            'version': dict_project.get('version', ''),
            'repository': None,
        }
        return {
            'licenses': licenses_from_package,
            'repo_suggestions': repo_suggestions,
            'package_details': package_details,
        }

    def lookup_providers(self, url, version=None):
        if 'pkg' in url or 'https' in url:
            if 'pkg' in url:
                purl = url
            else:
                purl = self._http_to_pkg(url)

            purl_object = PackageURL.from_string(purl)
            ns = purl_object.namespace
            n = purl_object.name
            v = purl_object.version

            # Identify licenses at providers
            providers = LicenseProviders().lookup_license_package(url, 'maven', ns, n, v)
            logging.debug(f'{self.__class__.__name__}:lookup_providers_impl providers: {providers}')
            return providers

        else:
            raise Exception(f'URL like {url} not yet supported for maven')

        return None

    def name(self):
        logging.debug(f'{self.__class__.__name__}:name()')
        return 'Maven'

    def lookup_url_impl(self, url, package_data=None, providers_data=None):
        logging.debug(f'{self.__class__.__name__}:lookup_url_impl {url}, {package_data is not None}, {providers_data is not None}')

        if not package_data:
            return None

        repo_data = None
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
