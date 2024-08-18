#!/bin/env python3

from argparse import RawTextHelpFormatter
import argparse
import logging

from lookup_license.lookuplicense import LookupLicense
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

def main():
    args = parse()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ll = LookupLicense()
        
    if args.func:
        try:
            ret = args.func(ll, args)
            print(str(ret))
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    main()
