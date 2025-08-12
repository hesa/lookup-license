import json

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FORMAT_JSON = "json"
FORMAT_TEXT = "text"

class FormatterFactory():

    @staticmethod
    def formatter(fmt):
        if fmt.lower() == FORMAT_JSON:
            return JsonFormatter()
        if fmt.lower() == FORMAT_TEXT:
            return TextFormatter()

class Formatter:

    def _ambig_response(self, lic):
        return lic['ambiguities'] == 0

    def format_license(self, lic, verbose=False):
        return None, None

    def format_error(self, exception, verbose=False):
        return None, None

    def format_lookup_urls(self, looked_up_urls, verbose=False):
        return None, None

class JsonFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        return json.dumps(lic), None

    def format_error(self, exception, verbose=False):
        return json.dumps(exception), None

    def format_lookup_urls(self, looked_up_urls, verbose=False):
        return json.dumps(looked_up_urls, indent=4), None

class TextFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        ambigs = []
        if not lic or (not lic.get('status')):
            return None, f'Could not identify license for {lic["provided"][:100]}.....'

        if verbose:
            ret = ['License:     ']
            for l in lic['normalized']:
                ret.append(f' * {l["license"]}  ({l["score"]})')
            ret.append(f'Ambiguities: {lic["ambiguities"]}')
        else:
            ret = [", ".join([l['license'] for l in lic['normalized']])]
        return '\n'.join(ret), None

    def format_error(self, exception, verbose=False):
        if verbose:
            import traceback
            err = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            return None, f'{exception}\n{err}'

        else:
            return None, f'{exception}'

    def _add_if_present(self, title, data, key, store):
        if data.get(key):
            store.append(f'{title:<20} {data.get(key)}')
        
    def format_lookup_urls(self, looked_up_urls, verbose=False):
        if not looked_up_urls:
            return '', 'No license data found.'
        if verbose:
            ret = []
            if 'meta' in looked_up_urls:
                meta = looked_up_urls['meta']
                if 'config_details' in meta:
                    config_details = meta['config_details']
                    self._add_if_present('Name:', config_details, 'name', ret)
                    self._add_if_present('Version:', config_details, 'version', ret)
                    self._add_if_present('Homepage:', config_details, 'homepage', ret)
                    self._add_if_present('Repository:', config_details, 'repository', ret)
                    #self._add_if_present('Source code zip:', meta, 'source_zip', ret)
            orig_url_title = 'Original url:'
            ret.append(f'{orig_url_title:<20} {looked_up_urls["provided"]}')
            ret.append('License identified in repository:')
            for url in looked_up_urls['details']['successful_urls']:
                ret.append(f' * {" AND ".join(url["license"])} <-- {url["url"]}')
            ret.append('License identified in package configuration:')
            if 'config_licenses' in looked_up_urls['details']:
                config_licenses = looked_up_urls['details']['config_licenses']
                if config_licenses:
                    for lic in config_licenses:
                        ret.append(f' * {lic["license"]} <-- {lic["url"]} ({lic["section"]})')
            return '\n'.join(ret), None
        return ' AND '.join(looked_up_urls['identified_license']), None
        
