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
        if not lic or (not lic.get('status')):
            return None, f'Could not identify license for {lic["provided"][:100]}.....'

        ret = []
        if verbose:
            ret.append('License:     ')
        for _lic in lic['normalized']:
            if lic['identification'] == 'flame':
                score_str = ''
                lic_str = _lic
            if lic['identification'] == 'lookup-license':
                lic_str = _lic['license']
                score_str = f'  score:{_lic["score"]}'
            if verbose:
                ret.append(f' * {lic_str}{score_str}')
            else:
                ret.append(f'{lic_str}')
        if verbose:
            ret.append(f'Ambiguities: {lic["ambiguities"]}')

        return '\n'.join(ret), None

    def format_error(self, exception, verbose=False):
        if verbose:
            import traceback
            err = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            return None, f'{exception}\n{err}'

        else:
            return None, f'{exception}'

    def _add(self, title, data, key, store):
        store.append(f'{title:<20} {data.get(key, "")}')

    def format_lookup_urls(self, looked_up_urls, verbose=False):
        if not looked_up_urls:
            return '', 'No license data found.'

        if 'identified_license_string' in looked_up_urls:
            identified_license_string = looked_up_urls['identified_license_string']
        else:
            identified_license_string = ''

        if verbose:
            ret = []
            if 'meta' in looked_up_urls:
                meta = looked_up_urls['meta']
                if 'config_details' in meta and meta['config_details']:
                    config_details = meta['config_details']
                    self._add('Name:', config_details, 'name', ret)
                    self._add('Version:', config_details, 'version', ret)
                    self._add('Homepage:', config_details, 'homepage', ret)

                    if meta.get('repository'):
                        ret.append(f'{"Repository:":<20} {meta.get("repository", "")}')
                    elif 'repository' in config_details:
                        self._add('Repository:', config_details, 'repository', ret)
                    else:
                        ret.append(f'{"Repository:":<20}')

            orig_url_title = 'Original url:'
            ret.append(f'{orig_url_title:<20} {looked_up_urls["provided"]}')
            ret.append(f'{"License identified:":<20} {identified_license_string}')
            ret.append('License identified in repository:')
            for url in looked_up_urls['details']['successful_urls']:
                ret.append(f' * {" AND ".join(url["license"])} <-- {url["url"]}')
            ret.append('License identified in package configuration:')
            if 'config_licenses' in looked_up_urls['details']:
                config_licenses = looked_up_urls['details']['config_licenses']
                if config_licenses:
                    for lic in config_licenses:
                        ret.append(f' * {lic["license"]} <-- {lic["url"]}')
            return '\n'.join(ret), None

        return identified_license_string, None
