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

class JsonFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        return json.dumps(lic), None

    def format_error(self, exception, verbose=False):
        return json.dumps(exception), None

class TextFormatter(Formatter):

    def format_license(self, lic, verbose=False):
        ambigs = []

        if not lic:
            return None, f'Invalid license {lic}'

        if lic['ambiguities'] != 0:
            ambigs = [a['description'] for a in lic['meta']['ambiguities']]
        if verbose:
            res_list = []
            res_list.append(f'Provided license:    {lic["provided"]}')
            res_list.append(f'Identification:      {lic["identification"]}')
            res_list.append(f'Ambiguities:         {lic["ambiguities"]}')
            if 'tried_urls' in lic:
                res_list.append(f'Tried urls:          {lic["tried_urls"]}')
                pass
            res_list.append('Normalized license:')
            for s in lic["normalized"]:
                res_list.append(f' * {s["license"]} / {s["score"]}')

            res = "\n".join(res_list)
        else:
            res_list = []
            for s in lic["normalized"]:
                res_list.append(s["license"])
            res = ", ".join(res_list)
        return res, "\n".join(ambigs)

    def format_error(self, exception, verbose=False):
        if verbose:
            import traceback
            err = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            return None, f'{exception}\n{err}'

        else:
            return None, f'{exception}'
