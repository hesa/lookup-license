from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from lookup_license.retrieve import Retriever
from lookup_license.license_db import LicenseDatabase

from packageurl import PackageURL

import json
import logging

class Pypi(LookupURL):

    def __init__(self):
        logging.debug("Pypi()")
        self.gitrepo = GitRepo()
        super().__init__()
    
    def _try_pypi_config_url(self, pypi_url):
        retriever = Retriever()
        retrieved_result = retriever.download_url(pypi_url)
        success = retrieved_result['success']
        if not success:
            return None
        decoded_content = retrieved_result['decoded_content']
        try:
            json_data = json.loads(decoded_content)
        except:
            return None

        #
        # Handle classifiers (in pypi JSON data)
        #
        licenses_from_config = []
        for classifier in json_data['info']['classifiers']:
            if 'license' in classifier.lower():
                license_object = {
                    'url': pypi_url,
                    'section': 'info.classifiers',
                    'license': classifier
                }
                licenses_from_config.append(license_object)

        #
        # Handle license variable (in pypi JSON data)
        #
        license_var = json_data['info'].get('license', None)
        if license_var:
                license_object = {
                    'url': pypi_url,
                    'section': 'info.license',
                    'license': license_var
                }
                licenses_from_config.append(license_object)
        #
        # Identify source code repository
        #
        repo_suggestions = []
        JSON_PATHS = [
            'info.project_urls.Source',
            'info.project_urls.Source Code',
            'info.project_urls.Code',
            'info.homepage',
            'info.project_urls.Homepage',
        ]
        # TODO: add version from JSON data to suggested URL
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
                    'config_url': pypi_url,
                    'config_path': complete_path,
                })

        repo_url = self._get_pypi_repo(json_data, JSON_PATHS)
        if not repo_url:
            repo_url = ''

        homepage = self._get_key('info.home_page', json_data)
        name = self._get_key('info.name', json_data)
        version = self._get_key('info.version', json_data)
            
        config_details = {
            'config_url': pypi_url,
            'homepage': homepage,
            'name': name,
            'version': version,
            'repository': repo_url
        }

        return {
            'licenses': licenses_from_config,
            'repo_suggestions': repo_suggestions,
            'config_details': config_details,
        }

    def _get_key(self, path, data):
        inner_data = data
        for sub_path in path.split('.'):
            if sub_path in inner_data:
                inner_data = inner_data[sub_path]
            else:
                return None
        return inner_data
    
    def _get_pypi_repo(self, paths, data):
        for path in paths:
            _data = self._get_key(path, data)
            if _data:
                return _data
    
    def lookup_url(self, url):

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
            # https
            pypi_urls = [
                url,
                f'{url}/json',
                f'{url}/json'.replace('/project/','/pypi/'),
            ]
        else:
            new_url = url.replace('@','/')
            new_url = new_url.replace('==','/')
            pypi_urls = [
                f'https://pypi.org/pypi/{new_url}/json'
            ]
            
            

        #
        # Loop through pypi urls, if data found in one url
        # scrape the configuration data and the repos suggested
        identified_pypi_data = None
        for pypi_url in pypi_urls:
            pypi_data = self._try_pypi_config_url(pypi_url)
            if pypi_data:
                # this pypi url had data
                # use the data below
                identified_pypi_data = pypi_data
                break
        if not identified_pypi_data:
            # TODO: add return data
            return None

        #
        # The data above contains suggestions for repository
        # urls. Loop through these and analyse them if data is found,
        # use the data from that repo
        uniq_repos = set([repo['repository'] for repo in identified_pypi_data['repo_suggestions']])
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
        licenses_from_config = identified_pypi_data['licenses']

        for lic in licenses_from_config:
            all_licenses.add(lic['license'])
            
        for lic in repo_data['identified_license']:
            all_licenses.add(lic)

        repo_data['provided'] = url
        repo_data['meta'] = {}
        repo_data['meta']['url_type'] = 'gem'
        repo_data['meta']['config_details'] = identified_pypi_data['config_details']
        repo_data['details']['suggestions'].append([pypi_url])
        repo_data['details']['config_licenses'] = licenses_from_config
        repo_data['identified_license'] = [LicenseDatabase.expression_license(x)['identified_license'] for x in all_licenses]

        # TODO: rmeove the output to file
        #with open('pypi.json', 'w') as fp:
        #    print(json.dump(repo_data, fp, indent=4))

        logging.debug("returning from pypi")
        return repo_data
    
