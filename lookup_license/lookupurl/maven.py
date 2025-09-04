# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo
from lookup_license.lookupurl.license_providers import LicenseProviders
from lookup_license.utils import get_keypath
from lookup_license.utils import contains

from lookup_license.retrieve import Retriever

from packageurl import PackageURL  # noqa: I900

import xmltodict

import json
import logging
import re

class Maven(LookupURL):

    def __init__(self):
        logging.debug("Pypi()")
        self.gitrepo = GitRepo()
        super().__init__()

    def lookup_package(self, url):
        pom_url = None
        if url.startswith('pkg:'):
            purl_object = PackageURL.from_string(url)
            ns = purl_object.namespace
            n = purl_object.name
            v = purl_object.version

            if contains(ns, ['mavencentral', 'mavengoogle', 'gradleplugin']):
                print('seems OK')
            else:
                print("uh ph...")

            print("url:    " + str(url))
            print("ns:     " + str(ns))

            # Figure out POM url
            if 'com.google' in ns or 'androidx' in ns or 'com.android' in ns:
                ns = purl_object.namespace.replace('.','/')
                pom_url = f'https://maven.google.com/{ns}/{n}/{v}/{n}-{v}.pom'
            else:
                ns = purl_object.namespace.replace('.','/')
                pom_url=f'https://repo1.maven.org/maven2/{ns}/{n}/{v}/{n}-{v}.pom'
        if url.startswith('https://'):
            raise Exception('https and maven not now!!')

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
        dict_project = data_dict['project']
        try:
            dict_licenses = data_project['licenses']
            for lic in dict_licenses.values():
                license_object = {
                    'url': pom_url,
                    'section': 'project.licenses',
                    'license': license_var,
                }
                licenses_from_package.append(license_object)
        except Exception as e:
            logging.debug(f'Could not find license in {pom_url}')

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
            'repo_suggestions': [],
            'package_details': package_details,
        }

    def lookup_providers(self, url, version=None):
        if 'pkg' in url:
            purl_object = PackageURL.from_string(url)
            ns = purl_object.namespace
            n = purl_object.name
            v = purl_object.version
            
            # Identify licenses at providers
            providers = LicenseProviders().lookup_license_package(url, 'maven', ns, n, v)
            logging.debug(f'{self.__class__.__name__}:lookup_providers_impl providers: {providers}')
            return providers

        elif 'https' in url:
            raise Exception(f'https not yet supported for maven')

        return None

    def name(self):
        logging.debug(f'{self.__class__.__name__}:name()')
        return 'Maven'

    def lookup_url_impl(self, url, package_data=None, providers_data=None):
        logging.debug(f'{self.__class__.__name__}:lookup_url_impl {url}, {package_data is not None}, {providers_data is not None}')
        return None

