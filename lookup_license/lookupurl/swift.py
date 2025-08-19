# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from packageurl import PackageURL
from lookup_license.retrieve import Retriever

import json
import logging
import re

class Swift(LookupURL):

    swiftpackageindex = None

    def __init__(self):
        logging.debug("Swift()")
        self.gitrepo = GitRepo()
        super().__init__()

    def _try_swift_config_url(self, url):
        pass

    def _is_purl(self, url):
        return url.startswith('pkg:')

    def _try_swiftpackageindex(self, url):
        #
        # Download git repo list for all indexed packages on swiftpackageindex.com
        # * URL comes from: https://swiftpackageindex.com/faq#how-does-it-work
        # * seems to list only github packages
        # TODO: write test to see if only github packages # noqa: T101
        packages_url = 'https://github.com/SwiftPackageIndex/PackageList/raw/refs/heads/main/packages.json'

        if not Swift.swiftpackageindex:
            retriever = Retriever()
            retrieved_result = retriever.download_url(packages_url)
            success = retrieved_result['success']
            if not success:
                return None
            decoded_content = retrieved_result['decoded_content']
            Swift.swiftpackageindex = decoded_content

        json_data = json.loads(decoded_content)

        # TODO: use the API to get the package meta data and from that the licenses # noqa: T101
        # * https://swiftpackageindex.com/<org>/collection.json
        # * licenses should be returned, see below
        # Note: only github.com repos are indexed at swiftpackageindex

        # If PURL url
        if 'pkg:' in url:
            purl_object = PackageURL.from_string(url)

            # if name in purl
            if purl_object.name:

                # if namespace in purl
                if purl_object.namespace:
                    reg_exp = f'https://github.com/{purl_object.namespace}/{purl_object.name}'
                else:
                    reg_exp = f'https://github.com/{purl_object.name}'

            if purl_object.version and ('latest' != purl_object.version and 'unspecified' != purl_object.version):
                pkg_version = purl_object.version
            else:
                pkg_version = None

        # swift package name
        else:
            reg_exp = url
            if '@' in url:
                splits = url.split('@')
                pkg_version = splits[1]
                reg_exp = f'/{splits[0]}'
            else:
                pkg_version = None

        # identify the urls matching the name
        # if 1 is found, return that one
        # * the above is true for https://swiftpackageindex.com/lokalise/lokalise-ios-framework
        urls = [pkg for pkg in json_data if reg_exp in pkg]
        if len(urls) == 0:
            logging.warning(f'Could not identify a repository for {url}')

        if len(urls) == 1:
            pass
        else:
            logging.warning(f'Could not identify one single repository for {url}. Found {len(urls)} urls: {urls}')

        if not urls:
            return None

        git_url = re.sub('.git$', '', urls[0])
        if pkg_version and ('latest' != pkg_version and 'unspecified' != pkg_version):
            git_url = f'{git_url}/tree/{pkg_version}'
        else:
            git_url = git_url

        config_details = {
            'config_url': packages_url,
            'homepage': '',
            'name': '',
            'version': '',
            'repository': git_url,
        }

        return {
            'licenses': [],
            'repo_suggestions': [{
                'repository': git_url,
                'config_url': '',
                'config_path': '',
            }],
            'config_details': config_details,
        }

    def _guess_urls(self, url):
        if not self._is_purl(url):
            return {
                'licenses': [],
                'repo_suggestions': [{
                    'repository': url.strip('/'),
                    'url': url,
                }],
            }

        url_suggestions = []

        # purl
        purl_object = PackageURL.from_string(url)
        p_namespace = purl_object.namespace
        p_version = purl_object.version

        # If github - compile repo url from the bits and pieces in the purl
        if p_namespace and 'github.com' in p_namespace:
            if p_version:
                git_url = f'https://{purl_object.namespace}/{purl_object.name}/tree/{purl_object.version}'
            else:
                git_url = f'https://{purl_object.namespace}/{purl_object.name}'

            url_suggestions.append({
                'repository': git_url,
                'url': url,
            })

        # ... what's next to the moon?
        # any other ways to identify repo?

        return {
            'licenses': [],
            'repo_suggestions': url_suggestions,
        }

    def lookup_url(self, url):
        # Try identifying the purl in swiftpackageindex.com
        swiftpackageindex_data = self._try_swiftpackageindex(url)
        if swiftpackageindex_data:
            data_suggestion = swiftpackageindex_data
        # Try identifying data using the data in the purl object
        else:
            data_suggestion = self._guess_urls(url)

        url_suggestions = data_suggestion['repo_suggestions']
        #
        # The 'urls' variable above contains suggestions for
        # repository urls. Loop through these and analyse them if data
        # is found, use the data from that repo
        uniq_repos = set([repo['repository'] for repo in url_suggestions]) # noqa: C403
        repo_data = None
        for repo in uniq_repos:
            repo_data = self.gitrepo.lookup_url(repo)
            success = repo_data['success']
            if success:
                break
            else:
                repo_data = None

        if not repo_data:
            return None

        licenses_object = self.gitrepo.licenses([], repo_data)
        repositories = []

        repo_data['provided'] = url
        repo_data['meta'] = {}
        repo_data['meta']['url_type'] = 'gem'
        repo_data['meta']['config_details'] = data_suggestion.get('config_details', {})
        repo_data['meta']['repository'] = ', '.join(repositories)
        repo_data['details']['config_licenses'] = licenses_object['config_license']
        repo_data['identified_license'] = licenses_object['identified_license']
        repo_data['identified_license_string'] = licenses_object['identified_license_string']

        return repo_data
