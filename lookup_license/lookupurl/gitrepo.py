# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lookup_license.lookupurl.lookupurl import LookupURL
from lookup_license.license_db import LicenseDatabase

from license_expression import ExpressionError

from packageurl import PackageURL

import logging

class GitRepo(LookupURL):

    def __init__(self):

        self.MAIN_BRANCHES = ['main', 'master', 'develop']
        self.LICENSE_FILES = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'license.md', 'COPYING', 'COPYING.txt', 'README.md', 'LICENSE-MIT', 'MIT-LICENSE']
        logging.debug("GitRepo()")
        super().__init__()

    def suggest_urls(self, url):
        return self.suggest_license_files(url)

    def raw_content_url(self, url):
        url = self.__fix_url(url)

# TODO: reintroduce, but simplify is_repo # noqa: T101

        if 'github' in url:
            url = url.replace("github.com", "raw.githubusercontent.com")
            if '/tree/main/' in url:
                url = url.replace('/tree/main/', '/refs/heads/main/')
            else:
                url = url.replace('/tree/', '/refs/tags/')
            url = url.replace('/blob/', '/')
            return url

        if 'gitlab' in url:
            return url.replace('/blob/', '/raw/')
        if 'freedesktop' in url:
            return url.replace('/tree/', '/plain/')
        raise Exception(f'Repo {url} not supported')

    def __fix_url(self, url):
        url = url.strip('/')
        if not url.startswith('http'):
            url = f'https://{url}'
        return url

    def has_branch(self, repo_url):
        if 'github' in repo_url:
            return ('/blob/' in repo_url or '/tree/' in repo_url)
        if 'freedesktop' in repo_url:
            return ('/tree/' in repo_url and '?' in repo_url)
        if 'gitlab' in repo_url:
            return '/tree/' in repo_url
        return None

    def OBSOLETE_is_file(self, repo_url):
        return not self.is_repo(repo_url)

    def OBSOLETE_is_repo(self, repo_url):
        import sys
        repo_url = self.__fix_url(repo_url)
        slashes = repo_url.count('/')

        if slashes == 3:
            if 'freedesktop' in repo_url:
                return True
        if slashes == 4:
            return True
        if slashes == 5:
            if 'freedesktop' in repo_url and ('/tree/?' in repo_url or '/tag/?' in repo_url):
                print("2 is_repo 5 True", file=sys.stderr)
                return True
            if 'freedesktop' in repo_url and ('/tree/' in repo_url or '/plain/' in repo_url):
                print("2 is_repo 5 False", file=sys.stderr)
                return False
        if slashes == 6:
            print("2 is_repo 6", file=sys.stderr)
            if 'gitlab' in repo_url:
                if '?' not in repo_url:
                    raise Exception(f'"{repo_url}" is a repo or file (having {slashes} slashes after stripping possible last / ')

                return False
            if 'github' in repo_url and 'tree' in repo_url:
                return True
            return False
        if slashes == 7:
            print("2 is_repo 7", file=sys.stderr)
            if 'github' in repo_url and 'refs' in repo_url:
                return True
            if 'gitlab' in repo_url and 'tree' in repo_url:
                return True
            return False
        if slashes == 8:
            print("2 is_repo 8: " + str(repo_url), file=sys.stderr)
            if 'github' in repo_url and 'refs' in repo_url:
                return False
            if 'github' in repo_url and 'blob' in repo_url:
                return False
            if 'gitlab' in repo_url and '/tree/' in repo_url:
                print("2 is_repo 81: " + str(repo_url), file=sys.stderr)
                return True
            if 'gitlab' in repo_url and 'blob' in repo_url:
                print("2 is_repo 82: " + str(repo_url), file=sys.stderr)
                return False
            if 'gitlab' in repo_url and 'raw' in repo_url:
                print("2 is_repo 83: " + str(repo_url), file=sys.stderr)
                return False
        if slashes == 9:
            print("2 is_repo 9: " + str(repo_url), file=sys.stderr)
            if 'gitlab' in repo_url:
                return False
            if 'github' in repo_url:
                return False

        print("2 is_repo EXECEPTION " + str(slashes), file=sys.stderr)
        raise Exception(f'Cannot determine if {repo_url} is a repo or file (having {slashes} slashes after stripping possible last / ')

    def _suggest_license_files(self, repo_url, url_source, branch=None):
        file_suggestions = []

        for license_file in self.LICENSE_FILES:
            license_url = None

            if not branch:
                if 'github' in repo_url:
                    license_url = self.__fix_url(f'{repo_url}/{license_file}')
            else:
                if 'github' in repo_url:
                    license_url = self.__fix_url(f'{repo_url}/blob/{branch}/{license_file}')

                if 'gitlab' in repo_url:
                    license_url = self.__fix_url(f'{repo_url}/blob/{branch}/{license_file}')

                if 'freedesktop' in repo_url:
                    license_url = self.__fix_url(f'{repo_url}/{license_file}?{branch}')

            if not license_url:
                return []

            raw_license_url = self.raw_content_url(license_url)
            file_suggestions.append({
                'license_raw_url': raw_license_url,
                'original_url': repo_url,
            })

            # Some git repos add "v" in front of the version
            # e.g "v0.1.0" but the release is called "0.0.0"
            # Add a 'v' in case
            if '/refs/tags/' in raw_license_url:
                raw_license_url = raw_license_url.replace('/refs/tags/', '/refs/tags/v')
                file_suggestions.append({
                    'license_raw_url': raw_license_url,
                    'original_url': repo_url,
                    'source': url_source,
                })

        return file_suggestions

    def suggest_license_files(self, repo_url, url_source='url', branches=None):
        has_branch = self.has_branch(repo_url)

        suggestions = []
        if has_branch:
            suggestions.append(self._suggest_license_files(repo_url, url_source))
        else:
            if not branches:
                branches = self.MAIN_BRANCHES
            for branch in branches:
                suggestions.append(self._suggest_license_files(repo_url, url_source, branch))
        return suggestions

    def lookup_url(self, url):
        if url.startswith('pkg:'):
            # purl
            purl_object = PackageURL.from_string(url)
            if purl_object.version:
                git_url = f'https://github.com/{purl_object.namespace}/{purl_object.name}/tree/{purl_object.version}'
            else:
                git_url = f'https://github.com/{purl_object.namespace}/{purl_object.name}'
        elif url.startswith('http'):
            # https
            git_url = url
        else:
            git_url = url

        suggestions = self.suggest_urls(git_url)
        ret = self.lookup_license_urls(url, suggestions)

        licenses_object = self.licenses([], ret)

        ret['meta'] = {}
        ret['meta']['url_type'] = 'pypi'
        ret['meta']['config_details'] = None
        ret['meta']['repository'] = "', '.join(repositories)"
        ret['details']['config_licenses'] = licenses_object['config_license']
        ret['identified_license'] = licenses_object['identified_license']
        ret['identified_license_string'] = licenses_object['identified_license_string']

        return ret

    def empty_data(self):
        return {
            'provided': '',
            'details': {
                'suggestions': [],
                'failed_urls': [],
                'successful_urls': [],
            },
            'identified_license': None,
            'success': False,
        }

    def gitrepo_repo(self, url):
        return ('/'.join(url.split('/')[:5]))

    def gitrepo_with_version(self, url, version):
        if not url:
            return None
        if 'github.com' in url:
            url = self.gitrepo_repo(url)
            ret = f'{url}/tree/{version}'
            logging.debug(f'gitrepo_with_version({url}, {version}) => {ret}')
            return ret
        logging.debug(f'gitrepo_with_version({url}, {version}) => None')

    def gitrepo_zip_file(self, url, version):
        if not url:
            return None
        if 'github.com' in url:
            return f'{url}/archive/refs/tags/{version}.zip'

    def repositories_from_details(self, repo_data, version):
        __repos = set()
        for __url in repo_data['details']['successful_urls']:
            orig_url = __url["original_url"]
            __repo = self.gitrepo_with_version(orig_url, version)
            __repos.add(__repo)
        return list(__repos)

    def licenses(self, config_data, repo_data):
        all_licenses = set()

        if config_data:
            licenses_from_config = config_data['licenses']
        else:
            licenses_from_config = []

        if licenses_from_config:
            for lic in licenses_from_config:
                all_licenses.add(lic['license'])

        if repo_data['identified_license']:
            for lic in repo_data['identified_license']:
                all_licenses.add(lic)

        try:
            identified_license = [LicenseDatabase.expression_license_identified(x) for x in all_licenses]
        except ExpressionError:
            identified_license = all_licenses

        try:
            identified_license_string = LicenseDatabase.summarize_license(all_licenses)
        except ExpressionError:
            identified_license_string = ', '.join(all_licenses)

        return {
            'config_license': licenses_from_config,
            'repo_licenses': repo_data['identified_license'],
            'all': list(all_licenses),
            'identified_license': identified_license,
            'identified_license_string': identified_license_string,
        }
