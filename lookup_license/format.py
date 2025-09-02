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

    def _add_value(self, title, value, store):
        store.append(f'{title:<20} {value}')

    def _add_key(self, title, data, key, store):
        self._add_value(title, data.get(key, ""), store)

    def _license_to_string(self, lic):
        if not lic:
            return '<no license found>'
        return lic

    def format_lookup_urls(self, looked_up_urls, verbose=False):
        if not looked_up_urls:
            return '', 'No license data found.'

        if 'identified_license_string' in looked_up_urls:
            identified_license_string = looked_up_urls['identified_license_string']
        else:
            identified_license_string = ''

        ret = []
        self._add_value('Identified license:', identified_license_string, ret)
        self._add_value('Supplied url:', looked_up_urls["provided"], ret)
        self._add_value('Supplied url type:', looked_up_urls["provided_type"], ret)

        if not verbose:
            return identified_license_string, None

        ret.append('')
        ret.append('Url details:')
        ret.append('------------')
        url_data = looked_up_urls.get('url_data')
        if url_data:
            if 'provided_type' in url_data:
                self._add_key('Provided:', url_data, 'provided', ret)
                self._add_key('Url type:', url_data, 'provided_type', ret)
                url_data = url_data['url_data']
            url_data_succ_urls = url_data['details']['successful_urls']

            licenses = ' AND '.join([u['license'] for u in url_data_succ_urls])
            self._add_value('License:', licenses, ret)

            ret.append('Identifications:')
            for succ_url in url_data_succ_urls:
                ret.append(f' * {succ_url["url"]}: {succ_url["license"]}')

        ret.append('')
        ret.append('Package details:')
        ret.append('----------------')
        package_data = looked_up_urls.get('package_data')
        if package_data:
            package_details = package_data.get('package_details')
            self._add_key('Name:', package_details, 'name', ret)
            self._add_key('Version:', package_details, 'version', ret)
            self._add_key('Type:', package_details, 'package_type', ret)
            self._add_key('Url:', package_details, 'package_url', ret)
            self._add_key('Homepage:', package_details, 'homepage', ret)
            #            self._add_key('Repository:', package_details, 'repository', ret)  # noqa: E800

            licenses = ' AND '.join([lic['license'] for lic in package_data['licenses']])
            self._add_value('License:', licenses, ret)

            ret.append('Identifications:')
            for lic in package_data['licenses']:
                ret.append(f' * {lic["url"]}: {lic["license"]}')

        ret.append('')
        ret.append('Providers details:')
        ret.append('------------------')
        ret.append('Identifications:')
        providers_data = looked_up_urls.get('providers_data')
        if providers_data:
            for provider in providers_data:
                lic = providers_data[provider]['license']
                prov_url = providers_data[provider]['data_url']
                ret.append(f' * {prov_url}: {lic}')

        return '\n'.join(ret), None
