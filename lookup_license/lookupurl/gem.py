# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from lookup_license.retrieve import Retriever
from lookup_license.lookupurl.fixes import fix_url

from packageurl import PackageURL

import json
import logging

class Gem(LookupURL):

    def __init__(self):
        logging.debug("Gem()")
        self.gitrepo = GitRepo()
        super().__init__()

    def _try_gem_config_url(self, gem_url):
        retriever = Retriever()
        retrieved_result = retriever.download_url(gem_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        json_data = json.loads(decoded_content)

        licenses_from_config = []
        #
        # Handle licenses variable (in gem JSON data)
        #
        license_var = json_data.get('licenses', None)
        if license_var:
            license_object = {
                'url': gem_url,
                'section': 'licenses',
                'license': ' AND '.join(license_var),
            }
            logging.info(f'found license {license_var} in {gem_url}')
            licenses_from_config.append(license_object)

        #
        # Identify source code repository
        #
        config_details = {}
        repo_suggestions = []
        JSON_PATHS = [
            'metadata.source_code_url',
            'metadata.source_code_uri',
            'source_code_uri',
            'homepage_uri',
        ]
        for complete_path in JSON_PATHS:
            inner_json_data = json_data
            for path in complete_path.split('.'):
                if path in inner_json_data:
                    inner_json_data = inner_json_data[path]
                else:
                    inner_json_data = None
                    break

            version = json_data["version"]

            repo_url_version = self.gitrepo.gitrepo_with_version(inner_json_data, version)
            if repo_url_version:
                repo_suggestions.append({
                    'repository': repo_url_version,
                    'config_url': gem_url,
                    'config_path': complete_path,
                })
                fixed_url = fix_url('gems', repo_url_version)
                if fixed_url:
                    repo_suggestions.append({
                        'repository': fixed_url,
                        'config_url': gem_url,
                        'config_path': complete_path,
                    })

        repo_url = json_data.get('source_code_uri')
        if not repo_url:
            if 'metadata' in json_data:
                metadata = json_data['metadata']
                if 'source_code_url' in metadata:
                    repo_url = metadata['source_code_url']

        config_details = {
            'config_url': gem_url,
            'homepage': json_data.get('homepage_uri', ''),
            'name': json_data.get('name', ''),
            'version': json_data.get('version', ''),
            'repository': repo_url,
        }

        return {
            'licenses': licenses_from_config,
            'repo_suggestions': repo_suggestions,
            'config_details': config_details,
        }

    def _find_latest_version(self, pkg_name):
        gem_url = f'https://rubygems.org/api/v1/gems/{pkg_name}.json'
        retriever = Retriever()
        retrieved_result = retriever.download_url(gem_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        json_data = json.loads(decoded_content)

        return json_data['version']

    def lookup_url(self, url):

        url = url.strip('/')

        if url.startswith('pkg:'):
            # purl
            purl_object = PackageURL.from_string(url)
            if purl_object.version:
                pkg_version = purl_object.version
            else:
                # TODO: download https://rubygems.org/api/v1/gems/PROJECT.json and identify latest version # noqa: T101
                pkg_version = f'{self._find_latest_version(purl_object.name)}'

            gem_urls = [
                f'https://rubygems.org/api/v2/rubygems/{purl_object.name}/versions/{pkg_version}.json',
            ]
            logging.info(f'suggested gem conf urls from pkg:: {gem_urls}')
        elif url.startswith('http'):
            # https

            # TODO: check if URL contains https://rubygems.org/api/v2/rubygems # noqa: T101
            gem_urls = [
                url,
                f'{url}/json',
                f'{url}/json'.replace('/project/', '/gem/'),
            ]
            logging.info(f'suggested gem conf urls from http:: {gem_urls}')
        else:
            # TODO: read license from url # noqa: T101
            new_url = url.replace('@', '/versions/')
            new_url = new_url.replace('==', '/')
            gem_urls = [
                f'https://rubygems.org/api/v2/rubygems/{new_url}.json',
            ]
            logging.info(f'suggested gem conf urls form *: {gem_urls}')

        #
        # Loop through gem urls,
        # * once data found in one url:
        # ** scrape the configuration data and the repos suggested
        # ** ... skip the remaining urls
        identified_gem_data = None
        for gem_url in gem_urls:
            gem_data = self._try_gem_config_url(gem_url)
            if gem_data:
                # this gem url had data
                # use the data below
                identified_gem_data = gem_data
                logging.info(f'found gems data via {gem_url}: {gem_data["repo_suggestions"]}')
                break
        if not identified_gem_data:
            # TODO: add return data # noqa: T101
            return None

        #
        # The data above contains suggestions for repository
        # urls. Loop through these and analyse them if data is found,
        # use the data from that repo
        uniq_repos = set()
        repo_data = None
        for repo in identified_gem_data['repo_suggestions']:
            if repo['repository'] in uniq_repos:
                continue
            uniq_repos.add(repo['repository'])
            repo_data = self.gitrepo.lookup_url(repo['repository'])
            success = repo_data['success']
            if success:
                break
            else:
                repo_data = None

        if not repo_data:
            repo_data = self.gitrepo.empty_data()

        licenses_object = self.gitrepo.licenses(identified_gem_data, repo_data)
        version = identified_gem_data['config_details']['version']
        repositories = self.gitrepo.repositories_from_details(repo_data, version)

        repo_data['provided'] = url
        repo_data['meta'] = {}
        repo_data['meta']['url_type'] = 'gem'
        repo_data['meta']['config_details'] = identified_gem_data['config_details']
        repo_data['meta']['repository'] = ', '.join(repositories)
        repo_data['details']['suggestions'].append([gem_url])
        repo_data['details']['config_licenses'] = licenses_object['config_license']
        repo_data['identified_license'] = licenses_object['identified_license']
        repo_data['identified_license_string'] = licenses_object['identified_license_string']

        return repo_data
