#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import logging
import sys

from lookup_license.lookuplicense import LookupLicense
from lookup_license.lookuplicense import LicenseTextReader
from lookup_license.ll_shell import LookupLicenseShell
from lookup_license.format import FormatterFactory
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

    parser.add_argument('-f', '--file',
                        action='store_true',
                        help='read license from file',
                        default=False)

    parser.add_argument('-u', '--url',
                        action='store_true',
                        help='read license from url',
                        default=False)

    parser.add_argument('-s', '--shell',
                        action='store_true',
                        help='interactive shell',
                        default=False)

    parser.add_argument('input',
                        type=str,
                        nargs="*",
                        help='license string, license file')
    return parser

def parse():
    return get_parser().parse_args()

def version_info(ll, args):
    return lookup_license.config.lookup_license_version

def license_file(ll, license_file):
    result = ll.lookup_license_file(license_file)
    return result

def license_url(ll, url):
    result = ll.lookup_license_url(url)
    return result

def license_text(ll, texts):
    result = ll.lookup_license_text(" ".join(texts))
    return result

def interactive_shell(ll):
    return LookupLicenseShell().cmdloop()

def main():
    args = parse()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ll = LookupLicense()

    try:
        if args.version:
            print(str(version_info(ll, args)))
        elif args.shell:
            return interactive_shell(ll)
        else:
            if args.input == []:
                lt_reader = LicenseTextReader()
                if args.file:
                    license_file_name = lt_reader.read_license_file()
                    result = license_file(ll, license_file_name)
                elif args.url:
                    license_url_name = lt_reader.read_license_url()
                    result = license_url(ll, license_url_name)
                else:
                    license_input = lt_reader.read_license_text()
                    result = license_text(ll, [license_input])
            elif args.input:
                if args.file:
                    result = license_file(ll, args.input[0])
                elif args.url:
                    result = license_url(ll, args.input[0])
                else:
                    result = license_text(ll, args.input)

            formatter = FormatterFactory.formatter("text")
            out, err = formatter.format_license(result, args.verbose)
            if err:
                print("error" + err, file=sys.stderr)
            print(out)
    except Exception as e:
        print(str(e), file=sys.stderr)


if __name__ == '__main__':
    main()
