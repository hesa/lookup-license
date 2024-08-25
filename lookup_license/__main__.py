#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import json
import logging

from lookup_license.lookuplicense import LookupLicense
from lookup_license.ll_shell import LookupLicenseShell
import lookup_license.config

def get_parser():

    parser = argparse.ArgumentParser(
        description=lookup_license.config.DESCRIPTION,
        epilog=lookup_license.config.EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information',
                        default=False)

    parser.add_argument('-V', '--version',
                        action='store_true',
                        help='output version information',
                        default=False)

    parser.set_defaults(which='help', func=version_info)

    subparsers = parser.add_subparsers(help='Sub commands')
    # license file
    parser_lf = subparsers.add_parser(
        'file', help='Identify license from license file')
    parser_lf.set_defaults(which='license', func=license_file)
    parser_lf.add_argument('file', type=str, help='license file')

    # license expressions
    parser_lf = subparsers.add_parser(
        'expression', help='Identify license from license expression')
    parser_lf.set_defaults(which='license-text', func=license_text)
    parser_lf.add_argument('file', type=str, help='license text')

    # interactive shell
    parser_sh = subparsers.add_parser(
        'shell', help='Start interactive shell')
    parser_sh.set_defaults(which='interactive_shell', func=interactive_shell)

    return parser
    

def parse():
    return get_parser().parse_args()

def version_info(ll, args):
    return lookup_license.config.lookup_license_version

def license_file(ll, args):
    result = ll.lookup_license_file(args.file)
    return result

def license_text(ll, args):
    result = ll.lookup_license_text(args.file)
    return result

def interactive_shell(ll, args):
    LookupLicenseShell().cmdloop()
    return None
def main():
    args = parse()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ll = LookupLicense()
        
    if args.func:
        try:
            ret = args.func(ll, args)
            if ret:
                print(json.dumps(ret, indent=4))
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    main()
