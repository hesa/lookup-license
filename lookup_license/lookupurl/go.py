# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.lookupurl.gitrepo import GitRepo

from lookup_license.retrieve import Retriever

from packageurl import PackageURL

import json
import logging

class Go(LookupURL):

    def __init__(self):
        logging.debug("Go()")
        self.gitrepo = GitRepo()
        super().__init__()

    def _repo_url(self, retriever, go_url):
        retrieved_result = retriever.download_url_raw(go_url)
        repo = False
        repo_url = None
        for line in retrieved_result.iter_lines():
            encoded_line = line.decode(encoding="utf-8")
            if '>Repository<' in encoded_line:
                repo = True
            if repo:
                if '<a href' in encoded_line:
                    href = encoded_line.split()[1]
                    print(">" + str(href) + "< 1")
                    url = href.split('=')[1].replace('"','')
                    print(">" + str(url) + "< 2")
                    repo = False
                    repo_url = url
        return repo_url
        
    def _license_files(self, retriever, go_url):
        retrieved_result = retriever.download_url_raw(f'{go_url}/?tab=licenses')
        
        license_files = []
        for line in retrieved_result.iter_lines():
            encoded_line = line.decode(encoding="utf-8")
            if '>Source: ' in encoded_line:
                print("line: " + encoded_line)
                lic_1 = encoded_line.split('>')[1]
                lic_2 = lic_1.split('<')[0]
                lic_file = lic_2.replace('Source: ', '')
                print(">" + str(lic_file) + "<")
                license_files.append(lic_file)
        return license_files

    def get_parameters_pkg_go_dev(self, url, version):
        logging.debug(f'{self.__class__.__name__}:get_parameters_pkg_go_dev {url}, {version}')
        stripped_url = url.replace('https://pkg.go.dev/', '')
        print("stripped: " + str(stripped_url))
        splits = stripped_url.split('/')
        print("splits: " + str(splits))
        repo_host = splits[0]
        repo_org = splits[1]
        name_splits = splits[2].split('@')
        pkg_name = name_splits[0]
        if len(name_splits) > 1:
            pkg_version = name_splits[1]
        else:
            pkg_version = None
        if len(splits) > 4:
            sub_dirs = '/'.join(splits[3:])
        
        ret = {
            'name': pkg_name,
            'namespace': f'go/golang/{repo_host}/{repo_org}',
            'version': pkg_version,
        }
        print(str(ret))
        print('https://api.clearlydefined.io/definitions/go/golang/github.com/typelate/check/v0.0.3')
        return ret
            
        
    def get_parameters(self, url, version):
        logging.debug(f'{self.__class__.__name__}:get_parameters {url}, {version}')
        if url.startswith('https://pkg.go.dev'):
            return self.get_parameters_pkg_go_dev(url, version)
        
        return {'name': 'go'}

    def lookup_package(self, url):
        logging.debug(f'{self.__class__.__name__}:lookup_package {url}')
        
    def _license_texts(self, retriever, go_url):
        retrieved_result = retriever.download_url_raw(f'{go_url}/?tab=licenses')
        
        license_texts = []
        license_text = []
        inside_license_text = False
        print()
        print()
        for line in retrieved_result.iter_lines():
            encoded_line = line.decode(encoding="utf-8")
            if inside_license_text:
                if '</pre>' in encoded_line:
                    inside_license_text = False
                    license_texts.append(license_text)
                    print("add license text ")
                    license_text = []
                else:
                    license_text.append(encoded_line)
            elif '<pre class="License-contents">' in encoded_line:
                print("license line: " + encoded_line)
                inside_license_text = True
                license_text.append(encoded_line.replace('<pre class="License-contents">', ''))
        return license_texts
                    
        
    def _try_go_package_page(self, go_url):
        print("try: " + str(go_url))
        
        if go_url.count('/') == 6:
            splits = go_url.split('/')

        
        
        retriever = Retriever()

        repo_url = self._repo_url(retriever, go_url)
        license_files = self._license_files(retriever, go_url)
        license_texts = self._license_texts(retriever, go_url)

        print("repo_url:     " + str(repo_url))
        print("license_files: " + str(license_files))
        print("license_texts: " + str(len(license_texts)))

        repo_suggestions = [{
                    'repository': repo_url,
                    'config_url': go_url,
                    'config_path': '',
                }]


        package_details = {
            'package_url': go_url,
            'package_type': self.name(),
            'homepage': '',
            'name': '',
            'version': '',
            'repository': repo_url,
        }

        return {
            'licenses': 'licenses_from_config',
            'repo_suggestions': repo_suggestions,
            'config_details': package_details,
        }

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

        url = url.strip('/')

        if url.startswith('pkg:'):
            print("HERE 1")
            # purl
            purl_object = PackageURL.from_string(url)
            go_urls = []
            if purl_object.version:
                go_urls.append(f'https://pkg.go.dev/{purl_object.name}/{purl_object.version}/json')
            else:
                go_urls.append(f'https://pkg.go.dev//{purl_object.name}/json')
        elif url.startswith('http'):
            print("HERE 2")
            # https
            go_urls = [
                url,
                f'{url}/json',
                f'{url}/json'.replace('/project/', '/go/'),
            ]
        else:
            print("HERE 3: " + str(url))
            go_urls = [
                f'https://pkg.go.dev/{url}',
            ]

            print("HERE 3: " + str(go_urls))

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
        if not identified_go_data:
            # TODO: add return data # noqa: T101
            return None

        #
        # The data above contains suggestions for repository
        # urls. Loop through these and analyse them if data is found,
        # use the data from that repo
        uniq_repos = set([repo['repository'] for repo in identified_go_data['repo_suggestions']]) # noqa: C403
        repo_data = None
        for repo in uniq_repos:
            print("Look up repo: " + repo)
            repo_data = self.gitrepo.lookup_url(repo)
            print("Look up repo: " + repo + ": " + str(repo_data))
            success = repo_data['success']
            if success:
                break
            else:
                repo_data = None

        if not repo_data:
            repo_data = self.gitrepo.empty_data()

        licenses_object = self.gitrepo.licenses(identified_go_data, repo_data)
        version = identified_go_data['config_details']['version']
        repositories = self.gitrepo.repositories_from_details(repo_data, version)

        repo_data['provided'] = url
        repo_data['meta'] = {}
        repo_data['meta']['url_type'] = 'go'
        repo_data['meta']['config_details'] = identified_go_data['config_details']
        repo_data['meta']['repository'] = ', '.join(repositories)
        repo_data['details']['suggestions'].append([go_url])
        repo_data['details']['config_licenses'] = licenses_object['config_license']
        repo_data['identified_license'] = licenses_object['identified_license']
        repo_data['identified_license_string'] = licenses_object['identified_license_string']

        return repo_data
