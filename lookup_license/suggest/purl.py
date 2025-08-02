from packageurl import PackageURL
from packageurl.contrib import purl2url

from lookup_license.suggest.gitrepo import GitRepo


class Purl:

    def __init__(self):
        self.gitrepo = GitRepo()

        pass

    def _github_repo_url(self, purl):
        """
        Return a github repo URL from the `purl` string.
        """
        purl_data = PackageURL.from_string(purl)
        purl_type = purl_data.type
        namespace = purl_data.namespace
        name = purl_data.name
        version = purl_data.version
        qualifiers = purl_data.qualifiers

        if not name:
            return

        if not namespace:
            print("NAME SPACE MISSING")

        if purl_type == 'swift':
            repo_url = f"https://{namespace}/{name}"            
        else:
            repo_url = f"https://github.com/{namespace}/{name}"

        print(" ---------------------------------- 1.1 " + str(purl_data.to_dict()))
        print(" ---------------------------------- 1.1 " + purl_type)
        print(" ---------------------------------- 1.1 " + repo_url)
        if version:
            print(" ---------------------------------- 1.2 " + repo_url)
            url_parts = repo_url.split('/')
            for url in url_parts:
                print (" * " + url)
            version_prefix = qualifiers.get('version_prefix', '')
            repo_url = f'{'/'.join(url_parts[:5])}/tree/{version_prefix}{version}'
            print(" ---------------------------------- 1.2 " + repo_url)

        print("IS NAJS " + str(repo_url))
        return repo_url

    def _guess_repo_url(self, purl):
        print("calling PackageUrl")
        purl_object = PackageURL.from_string(purl)
        print("got: " + str(purl_object.to_dict()))
        purl_type = purl_object.type
        purl_namespace = purl_object.namespace
        purl_name = purl_object.name
        purl_version = purl_object.version
        print("....  type: \"" + str(purl_type) + "\"")

        if purl_type == 'pypi':
            print(" ---------------------------------- PYPI")
            
        if purl_type == 'swift':
            print(" ---------------------------------- 3")
            return self._github_repo_url(purl)
        elif purl_type == 'github' or (purl_namespace and 'github' in purl_namespace):
            print(" ---------------------------------- 1")
            return self._github_repo_url(purl)
        elif purl_type == 'pypi':
            print(" ---------------------------------- PYPI")
            pypi_url = f'https://pypi.org/pypi/{purl_name}/json'
            print(" ---------------------------------- PYPI: " + pypi_url)
            
        else:
            print(" ---------------------------------- 2")
            # try using purl2url
            repo_url = purl2url.get_repo_url(purl)
            
            print(f'Purl type "{purl_type}" not supported: {purl_object}')
            if not repo_url :
                raise Exception(f'Could not get repo url for {purl}')
        print("hat??")
        print(str(purl_object))
        return f'github.com/{purl_namespace.replace("github.com/","")}/{purl_name}'

    def repo_url(self, purl):
        print("ru calling _")
        return self._guess_repo_url(purl)
        
    
    def suggest_urls(self, purl):
        repo_url = self.repo_url(purl)

        if repo_url:
            return self.gitrepo.suggest_license_files(repo_url)
        
        return None
