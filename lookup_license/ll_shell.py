# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import cmd
import sys
from lookup_license.lookuplicense import LookupLicense
from lookup_license.lookuplicense import LicenseTextReader
from lookup_license.format import FormatterFactory

ll = LookupLicense()

class LookupLicenseShell(cmd.Cmd):
    intro = 'Welcome to the LookupLicense shell. Type help or ? to list commands.\n'
    prompt = 'LookupLicense> '
    file = None

    def __init__(self, verbose=False):
        cmd.Cmd.__init__(self)
        self.verbose_mode = verbose
        self.license_reader = None
        self.formatter = None

    def output(self, string, end="\n"):
        print(string, end=end)

    def verbose(self, string, end="\n"):
        if self.verbose_mode:
            print(string, end=end)

    def do_exit(self, arg):
        """Exit the interactive shell"""
        return True

    def do_EOF(self, args):
        """Sending EOF (e.g. Cotrnol-d) will exit the interactive shell"""
        return True

    def emptyline(self):
        return self.do_text(None)

    def do_text(self, arg):
        """Provide a license text for license lookup. After issuing "text", copy/paste the license text to input (stdin) and send EOF (e.g. by pressing Control-d) and type ENDOFLICENSETEXT."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        license_text = self.license_reader.read_license_text()
        self.verbose(f'read {len(license_text)} charcters, looking up the license')
        result = ll.lookup_license_text(license_text)
        self.__output_result(result)

    def do_file(self, arg):
        """Provide a file name (containing a license text) for license lookup. After issuing "file", write the filename /paste the license text to input (stdin) and press enter."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        filename = self.license_reader.read_license_file()
        self.verbose(f'Read {filename} charcters from {filename}, looking up the license')
        result = ll.lookup_license_file(filename)
        self.__output_result(result)

    def do_verbose(self, arg):
        """Make the interaction more verbose."""
        self.verbose_mode = True

    def do_silent(self, arg):
        """Make the interaction less verbose (default)."""
        self.verbose_mode = False

    def __output_result(self, result):
        if self.verbose_mode:
            if not self.formatter:
                self.formatter = FormatterFactory.formatter("text")
            out, err = self.formatter.format_license(result)
            if err:
                print("error" + err, file=sys.stderr)
            print(out)
        else:
            print(str(result['normalized']))


if __name__ == '__main__':
    LookupLicenseShell().cmdloop()
