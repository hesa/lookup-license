from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from lookup_license.retrieve import Retriever
from lookup_license.license_db import LicenseDatabase

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
        try:
            json_data = json.loads(decoded_content)
        except:
            return None

        licenses_from_config = []
        #
        # Handle licenses variable (in gem JSON data)
        #                
        license_var = json_data.get('licenses', None)
        if license_var:
                license_object = {
                    'url': gem_url,
                    'section': 'licenses',
                    'license': license_var
                }
                licenses_from_config.append(license_object)

        #
        # Identify source code repository
        #
        repo_suggestions = []
        JSON_PATHS = [
            'metadata.source_code_url',
            'homepage_uri',
            'source_code_uri',
        ]
        for complete_path in JSON_PATHS:
            inner_json_data = json_data
            for path in complete_path.split('.'):
                if path in inner_json_data:
                    inner_json_data = inner_json_data[path]
                else:
                    inner_json_data = None
                    break

            # TODO: add version from JSON data to suggested URL
            if inner_json_data:
                repo_suggestions.append({
                    'repository': inner_json_data,
                    'config_url': gem_url,
                    'config_path': complete_path,
                })

        return {
            'licenses': licenses_from_config,
            'repo_suggestions': repo_suggestions,
        }


    def _find_latest_version(self, pkg_name):
        gem_url = f'https://rubygems.org/api/v1/gems/{pkg_name}.json'
        retriever = Retriever()
        retrieved_result = retriever.download_url(gem_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        try:
            json_data = json.loads(decoded_content)
        except:
            return None

        return json_data['version']
    
    def lookup_url(self, url):

        url = url.strip('/')
        
        if url.startswith('pkg:'):
            # purl
            purl_object = PackageURL.from_string(url)
            if purl_object.version:
                pkg_version = purl_object.version
            else:
                # TODO: download https://rubygems.org/api/v1/gems/PROJECT.json and identify latest version
                pkg_version = f'{self._find_latest_version(purl_object.name)}'

            gem_urls = [
                f'https://rubygems.org/api/v2/rubygems/{purl_object.name}/versions/{pkg_version}.json'
            ]
        elif url.startswith('http'):
            # https
            gem_urls = [
                url,
                f'{url}/json',
                f'{url}/json'.replace('/project/','/gem/'),
            ]
        else:
            new_url = url.replace('@','/')
            new_url = new_url.replace('==','/')
            gem_urls = [
                f'https://gem.org/gem/{new_url}/json'
            ]
            
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
                break
        if not identified_gem_data:
            # TODO: add return data
            return None

        #
        # The data above contains suggestions for repository
        # urls. Loop through these and analyse them if data is found,
        # use the data from that repo
        uniq_repos = set([repo['repository'] for repo in identified_gem_data['repo_suggestions']])
        repo_data = None
        for repo in uniq_repos:
            repo_data = self.gitrepo.lookup_url(repo)
            success = repo_data['success']
            if success:
                break
            else:
                repo_data = None

        if not repo_data:
            #TODO: addreturn data
            return None

        all_licenses = set()        
        licenses_from_config = identified_gem_data['licenses']

        for lic_list in licenses_from_config:
            for lic in lic_list['license']:
                all_licenses.add(lic)
            
        for lic in repo_data['identified_license']:
            all_licenses.add(lic)

        repo_data['provided'] = url
        repo_data['details']['suggestions'].append([gem_url])
        repo_data['details']['config_licenses'] = licenses_from_config
        repo_data['identified_license'] = [LicenseDatabase.expression_license(x)['identified_license'] for x in all_licenses]

        # TODO: rmeove the output to file
        #with open('gem.json', 'w') as fp:
        #    print(json.dump(repo_data, fp, indent=4))

        logging.debug("returning from gem")
        return repo_data
    
