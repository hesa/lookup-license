# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

module_name = 'lookup_license'
module_author = 'hesa'
lookup_license_version = "0.1.30"

default_minimum_score = 0.9
http_timeout = 10 # seconds

module_name = 'lookup_license'

short_description = 'Python tool to identify license from license text, urls, license names and package names.'

DESCRIPTION = """lookup-license

DESCRIPTION
  Python tool to identify license from license text, urls, license names and package names.
"""

EPILOG = """
AUTHOR
  Henrik Sandklef

PROJECT SITE
  https://github.com/hesa/lookup-license

REPORTING BUGS
  File a ticket at https://github.com/hesa/lookup-license/issues

COPYRIGHT
  Copyright (c) 2025 Henrik Sandklef<hesa@sandklef.com>.
  License GPL-3.0-or-later

ATTRIBUTION
  * https://github.com/aboutcode-org/scancode-toolkit - to identify license from license text
  * https://github.com/hesa/foss-licenses - to identify license frorm "weird" names
"""
