from lookup_license.lookupurl.lookupurl import LookupURL


class LicenseProvider():

    def name(self):
        return None

    def lookup_license(self, url):
        data = self.lookup_license_impl(url)
        data['provider'] = self.name()
        data['url'] = url
        data['status'] = data['license'] is not None

        return data

    def lookup_license_package(self, orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None):
        data = self.lookup_license_package_impl(orig_url, pkg_type, pkg_namespace, pkg_name, pkg_version, pkg_qualifiers=None, pkg_subpath=None)
        data['provider'] = self.name()
        data['url'] = orig_url
        data['status'] = data['license'] is not None
        return data
    
