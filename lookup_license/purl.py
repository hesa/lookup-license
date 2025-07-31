from packageurl import PackageURL

from lookup_license.gitrepo import GitRepo

class Purl:

    def __init__(self):
        pass

    def _guess_purl_github(self, purl, purl_object):
        type = purl_object['type']
        namespace = purl_object['namespace']
        name = purl_object['name']
        version = purl_object['version']

        print(str(purl_object))
        git_repo_url = f'{type}.com/{namespace}/{name}'
        print(str(git_repo_url))
        gitrepo = GitRepo()
        suggestions = gitrepo.suggest_license_files(git_repo_url, version)
        print("SUGGESTIONS: " + str(suggestions))
        import sys
        sys.exit(1)
        urls = []
        for tag in ['refs/tags']:
            for license_file in LICENSE_FILES:
                gh_url = f'https://raw.githubusercontent.com/{namespace}/{name}/{tag}/{version}/{license_file}'
                urls.append(gh_url)
        return urls

    
    def suggest_license_files(self, purl):
        purl_object = PackageURL.from_string(purl).to_dict()
        purl_type = purl_object['type']
        
        if purl_type == 'github':
            return self._guess_purl_github(purl, purl_object)

        return None
