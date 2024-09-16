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

class JsonFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        return json.dumps(lic), None

class TextFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        ambigs = []
        if lic['ambiguities'] != 0:
            ambigs = [a['description'] for a in lic['meta']['ambiguities']]
        if verbose:
            res_list = []
            res_list.append(f'Identification: {lic["identification"]}')
            res_list.append(f'Provided:       {lic["provided"]}')
            res_list.append(f'Ambiguities:    {lic["ambiguities"]}')
            if 'tried_urls' in lic:
                res_list.append(f'Tried urls:     {lic["tried_urls"]}')
            res_list.append(f'Normalized:     {lic["normalized"]}')
                
            res = "\n".join(res_list)
        else:
            res = "\n".join(lic['normalized'])
        return res, "\n".join(ambigs)
