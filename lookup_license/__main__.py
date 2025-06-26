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

    parser.add_argument('-gh', '--github',
                        action='store_true',
                        help='try to read license from github repo url',
                        default=False)

    parser.add_argument('-s', '--shell',
                        action='store_true',
                        help='interactive shell',
                        default=False)

    parser.add_argument('--validate-spdx',
                        action='store_true',
                        help='validate that the resulting license expression is an SPDX license expression',
                        default=False)

    parser.add_argument('--minimum-score',
                        type=str,
                        help=f'minimum required score when identifying a license from license text, defaults to {lookup_license.config.default_minimum_score}',
                        default=lookup_license.config.default_minimum_score)

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

def github_url(ll, url):
    result = ll.lookup_github_url(url)
    return result

def license_text(ll, texts, minimum_score):
    result = ll.lookup_license_text(" ".join(texts), minimum_score)
    return result

def interactive_shell(ll):
    return LookupLicenseShell().cmdloop()

def validate(ll, args, expr):
    if args.validate_spdx:
        return ll.validate(" AND ".join(expr['normalized']))


def main():
    args = parse()

    if args.verbose:
        logging.getLogger(lookup_license.config.module_name).setLevel(logging.DEBUG)

    ll = LookupLicense()

    try:
        if args.version:
            print(str(version_info(ll, args)))
        elif args.shell:
            return interactive_shell(ll)
        else:
            err = None
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
                    result = license_text(ll, [license_input], float(args.minimum_score))
            elif args.input:
                if args.file:
                    result = license_file(ll, args.input[0])
                elif args.github:
                    result = github_url(ll, args.input[0])
                    if not result['normalized']:
                        err = f'Could not get license information from github url "{args.input[0]}".'
                        out = ''
                elif args.url:
                    result = license_url(ll, args.input[0])
                else:
                    result = license_text(ll, args.input, float(args.minimum_score))

            if not err:
                formatter = FormatterFactory.formatter("text")
                try:
                    validate(ll, args, result)
                    out, err = formatter.format_license(result, args.verbose)
                except Exception as e:
                    out = ""
                    out, err = formatter.format_error(e, args.verbose)

            if err:
                print("error: " + err, file=sys.stderr)
            if out:
                print(out)

            if err:
                sys.exit(1)
            sys.exit(0)

    except Exception as e:
        print(str(e), file=sys.stderr)


if __name__ == '__main__':
    main()
