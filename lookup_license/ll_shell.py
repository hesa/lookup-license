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
    prompt = '>>> '
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

    def __handle_error(self, error):
        print(str(error))

    def do_exit(self, arg):
        """Exit the interactive shell"""
        return True

    def do_EOF(self, args):
        """Sending EOF (e.g. Control-d) will exit the interactive shell"""
        return True

    def emptyline(self):
        return self.do_text(None)

    def do_text(self, arg):
        """Provide a license text for license lookup. After issuing "text", copy/paste the license text to input (stdin) and send EOF (e.g. by pressing Control-d) and type ENDOFLICENSETEXT."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        license_text = self.license_reader.read_license_text()
        self.verbose(f'read {len(license_text)} characters, looking up the license')
        try:
            result = ll.lookup_license_text(license_text)
            self.__output_result(result)
        except Exception as e:
            self.__handle_error(e)

    def do_file(self, arg):
        """Provide a file name (containing a license text) for license lookup. After issuing "file", write the filename /paste the license text to input (stdin) and press enter."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        filename = self.license_reader.read_license_file()
        self.verbose(f'Read {filename}, looking up the license')
        try:
            result = ll.lookup_license_file(filename)
            self.__output_result(result)
        except Exception as e:
            self.__handle_error(e)

    def do_url(self, arg):
        """Provide a URL (containing a license text) for license lookup. After issuing "url", write the full URL/path to the license file to input (stdin) and press enter."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        url = self.license_reader.read_license_url()
        self.verbose(f'Read {url}, looking up the license')
        try:
            result = ll.lookup_license_url(url)
            self.__output_result(result)
        except Exception as e:
            self.__handle_error(e)

    def do_github(self, arg):
        """Provide a GitHub repository URL for license lookup. After issuing "github", write the GitHub repository URL to input (stdin) and press enter."""
        if not self.license_reader:
            self.license_reader = LicenseTextReader()
        url = self.license_reader.read_license_url()
        self.verbose(f'Read {url}, looking up the license')
        try:
            result = ll.lookup_github_url(url)
            self.__output_result(result)
        except Exception as e:
            self.__handle_error(e)

    def do_verbose(self, arg):
        """Make the interaction more verbose."""
        self.verbose_mode = True

    def do_silent(self, arg):
        """Make the interaction less verbose (default)."""
        self.verbose_mode = False

    def __output_result(self, result):
        if not self.formatter:
            self.formatter = FormatterFactory.formatter("text")
        out, err = self.formatter.format_license(result, verbose=self.verbose_mode)
        if err:
            print("error" + err, file=sys.stderr)
        if out:
            print(out)


if __name__ == '__main__':
    LookupLicenseShell().cmdloop()
