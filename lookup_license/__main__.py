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
from lookup_license.lookupurl.factory import LookupURLFactory
from lookup_license.ll_shell import LookupLicenseShell
from lookup_license.format import FormatterFactory
from lookup_license.cache import LookupLicenseCache

import lookup_license.config

def get_parser():

    parser = argparse.ArgumentParser(
        description=lookup_license.config.DESCRIPTION,
        epilog=lookup_license.config.EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='output verbose information',
                        default=False)

    parser.add_argument('-V', '--version',
                        action='store_true',
                        help='output version information',
                        default=False)

    parser.add_argument('-of', '--output-format',
                        type=str,
                        default='text')

    parser.add_argument('-nc', '--no-cache',
                        action='store_true',
                        help='don\'t use cache ',
                        default=False)

    parser.add_argument('--clear-cache',
                        action='store_true',
                        help='clear the cache ',
                        default=False)

    parser.add_argument('-uc', '--update-cache',
                        action='store_true',
                        help='if the url is already in the cache, update with a new value. This will automatically disable using the cached values',
                        default=False)

    parser.add_argument('-f', '--file',
                        action='store_true',
                        help='read license from file',
                        default=False)

    parser.add_argument('-u', '--url',
                        action='store_true',
                        help='identify license (scanning content) from url',
                        default=False)

    parser.add_argument('--gitrepo',
                        action='store_true',
                        help='try to read license from license file from git repo url (no scanning)',
                        default=False)

    parser.add_argument('--purl',
                        action='store_true',
                        help='try to read license from license file url from purl/package url (no scanning)',
                        default=False)

    parser.add_argument('--swift',
                        action='store_true',
                        help='try to read license from license file url from purl/package url (no scanning)',
                        default=False)

    parser.add_argument('--pypi',
                        action='store_true',
                        help='try to read license from pypi package (no scanning)',
                        default=False)

    parser.add_argument('--gem',
                        action='store_true',
                        help='try to read license from rubygems.org package (no scanning)',
                        default=False)

    parser.add_argument('--maven',
                        action='store_true',
                        help='try to read license from maven (no scanning)',
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
    # in case it is a url to an HTML page
    result = LookupURLFactory.lookupurl('url').lookup_url(url)
    return result

def gitrepo_url(ll, url):
    result = LookupURLFactory.lookupurl('git').lookup_url(url)
    return result

def purl_url(ll, url):
    result = LookupURLFactory.lookupurl_url(url).lookup_url(url)
    return result

def swift_url(ll, url):
    result = LookupURLFactory.lookupurl('swift').lookup_url(url)
    return result

def pypi_url(ll, url):
    result = LookupURLFactory.lookupurl('pypi').lookup_url(url)
    return result

def gem_url(ll, url):
    result = LookupURLFactory.lookupurl('gem').lookup_url(url)
    return result

def maven_url(ll, url):
    result = LookupURLFactory.lookupurl('maven').lookup_url(url)
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

    logging.basicConfig(force=True, level=logging.WARNING)
    if args.verbose > 1:
        logging.basicConfig(force=True, level=logging.INFO)
    if args.verbose > 2:
        logging.basicConfig(force=True, level=logging.DEBUG)

    if args.clear_cache:
        LookupLicenseCache().clear()
        logging.info('Cache cleared')
        sys.exit(0)

    if args.update_cache:
        LookupLicenseCache().set_update_mode(args.update_cache)
    elif args.no_cache:
        LookupLicenseCache().disable()

    ll = LookupLicense()

    try:
        if args.version:
            print(str(version_info(ll, args)))
        elif args.shell:
            return interactive_shell(ll)
        else:
            formatter = FormatterFactory.formatter(args.output_format)

            # no command line arguments
            # read license text from stdin
            if args.input == []:
                lt_reader = LicenseTextReader()
                if args.file:
                    license_file_name = lt_reader.read_license_file()
                    result = license_file(ll, license_file_name)
                    out, err = formatter.format_license(result, args.verbose)
                elif args.url:
                    license_url_name = lt_reader.read_license_url()
                    result = license_url(ll, license_url_name)
                    out, err = formatter.format_license(result, args.verbose)
                else:
                    license_input = lt_reader.read_license_text()
                    result = license_text(ll, [license_input], float(args.minimum_score))
                    out, err = formatter.format_license(result, args.verbose)

            # check command line arguments
            elif args.input:
                err = None
                if args.file:
                    result = license_file(ll, args.input[0])
                    out, err = formatter.format_license(result, args.verbose)
                elif args.gitrepo:
                    result = gitrepo_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.url:
                    result = license_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.purl:
                    result = purl_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.swift:
                    result = swift_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.pypi:
                    result = pypi_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.gem:
                    result = gem_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                elif args.maven:
                    result = maven_url(ll, args.input[0])
                    out, err = formatter.format_lookup_urls(result, args.verbose)
                else:
                    result = license_text(ll, args.input, float(args.minimum_score))
                    out, err = formatter.format_license(result, args.verbose)
            if not err:
                try:
                    validate(ll, args, result)
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
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == '__main__':
    main()
