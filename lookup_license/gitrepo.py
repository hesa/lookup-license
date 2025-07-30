

class GitRepo:

    def __init__(self):
        self.MAIN_BRANCHES = ['main', 'master', 'develop' ]
        self.LICENSE_FILES = ['LICENSE', 'LICENSE.txt', 'COPYING', 'COPYING.txt']
        
    def raw_content_url(self, url):
        url = self.__fix_url(url)
        if self.is_repo(url):
            raise Exception(f'Raw url to a repository ({repo_url}) not supported')
        
        if 'github' in url:
            return url.replace("github.com", "raw.githubusercontent.com").replace('/blob/', '/')
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
            return '/blob/' in repo_url
        if 'freedesktop' in repo_url:
            return ('/tree/' in repo_url and '?' in repo_url)
        if 'gitlab' in repo_url:
            return '/tree/' in repo_url
        raise Exception(f'Repo {repo_url} not supported')

    def is_file(self, repo_url):
        return not self.is_repo(repo_url)

    def is_repo(self, repo_url):
        import sys
        print("1 is_repo: " + str(repo_url), file=sys.stderr)
        repo_url = self.__fix_url(repo_url)
        print("2 is_repo: " + str(repo_url), file=sys.stderr)
        slashes = repo_url.count('/')

        if slashes == 3:
            print("2 is_repo 3", file=sys.stderr)
            if 'freedesktop' in repo_url:
                return True
        if slashes == 4:
            print("2 is_repo 4", file=sys.stderr)
            return True
        if slashes == 5:
            print("2 is_repo 5 " + repo_url, file=sys.stderr)
            if 'freedesktop' in repo_url and ('/tree/?' in repo_url or '/tag/?' in repo_url):
                print("2 is_repo 5 True", file=sys.stderr)
                return True
            if 'freedesktop' in repo_url and ('/tree/' in repo_url or '/plain/' in repo_url):
                print("2 is_repo 5 False", file=sys.stderr)
                return False
        if slashes == 6:
            print("2 is_repo 6", file=sys.stderr)
            if 'gitlab' in repo_url:
                if not '?' in repo_url:
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

    def _suggest_license_files(self, repo_url, branch=None):
        file_suggestions = []

        
        for license_file in self.LICENSE_FILES:
            license_url = None
            
            if 'github' in repo_url:
                license_url = self.__fix_url(f'{repo_url}/blob/{branch}/{license_file}')

            if 'gitlab' in repo_url:
                license_url = self.__fix_url(f'{repo_url}/blob/{branch}/{license_file}')
                    
            if 'freedesktop' in repo_url:
                license_url = self.__fix_url(f'{repo_url}/{license_file}?{branch}')
                    
            if not license_url:
                raise Exception(f'Guessing license file for {repo_url} is not implemented')
            
            raw_license_url = self.raw_content_url(license_url)
            file_suggestions.append(raw_license_url)
        
        return file_suggestions
    
    def suggest_license_files(self, repo_url):
        if not self.is_repo(repo_url):
            raise Exception(f'"{repo_url}" is not a repository url')

        suggestions = []
        if self.has_branch(repo_url):
            suggestions.append(self._suggest_license_files(repo_url))
        else:
            for branch in self.MAIN_BRANCHES:
                suggestions.append(self._suggest_license_files(repo_url, branch))
        return suggestions
