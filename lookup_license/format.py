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

    def format_license(self, lic):
        return None, None

class JsonFormatter(Formatter):

    def format_license(self, lic):
        return json.dumps(lic), self._ambig_response(lic)

class TextFormatter(Formatter):

    def format_license(self, lic):
        ambigs = []
        if lic['ambiguities'] != 0:
            ambigs = [a['description'] for a in lic['meta']['ambiguities']]
        return "\n".join(lic['normalized']), "\n".join(ambigs)
