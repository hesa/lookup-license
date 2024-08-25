# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import cmd
import sys
from lookup_license.lookuplicense import LookupLicense

ll = LookupLicense()

class LookupLicenseShell(cmd.Cmd):
    intro = 'Welcome to the LookupLicense shell. Type help or ? to list commands.\n'
    prompt = 'LookupLicense> '
    file = None

    def __init__(self, verbose=False):
        cmd.Cmd.__init__(self)
        #global ll
        #self.ll = ll
        self.verbose = verbose

    def output(self, string, end="\n"):
        if self.verbose:
            print(string, end=end)
        
    def edo_help(self, arg):
        ''
        print("helpie...")

    def do_exit(self, arg):
        'Exit the interactive shell'
        return True

    def do_EOF(self, args):
        'Sending EOF (e.g. Cotrnol-d) will exit the interactive shell'
        return True

    def do_text(self, arg):
        'Provide a license text for license lookup. After issuing "text", copy/paste the license text to input (stdin) and send EOF (e.g. by pressing Control-d) and type ENDOFLICENSETEXT.'
        self.output('Enter license text and press Control-d.')
        license_lines = []
        while True:
            try:
                line = input()
                #print(str(line))
            except EOFError:
                break
            if line == "ENDOFLICENSETEXT":
                break
            license_lines.append(line)

        license_text = '\n'.join(license_lines)
        self.output(f'read {len(license_text)} charcters, looking up the license')
        res = ll.lookup_license_text(license_text)
        print(str(res['normalized']))

    def do_file(self, arg):
        'Provide a file name (containing a license text) for license lookup. After issuing "file", write the filename /paste the license text to input (stdin) and press enter.'
        self.output('Enter license file: ', end="\n")
        filename = input()
        self.output(f'Read {filename} charcters from {filename}, looking up the license')
        res = ll.lookup_license_file(filename)
        print(str(res['normalized']))

    def do_verbose(self, arg):
        'Make the interaction more verbose.'
        self.verbose = True

    def do_silent(self, arg):
        'Make the interaction less verbose (default).'
        self.verbose = False

if __name__ == '__main__':
    LookupLicenseShell().cmdloop()
