# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os

fixes = None

SCRIPT_DIR = os.path.dirname(__file__)
LOOKUP_LICENSE_DIR = os.path.join(SCRIPT_DIR, '..')
LOOKUP_LICENSE_DATA_DIR = os.path.join(LOOKUP_LICENSE_DIR, 'data')
LOOKUP_LICENSE_FIXES_FILE = os.path.join(LOOKUP_LICENSE_DATA_DIR, 'url-fixes.json')

def fix_url(ecosystem, url):
    global fixes
    if not fixes:
        with open(LOOKUP_LICENSE_FIXES_FILE) as fp:
            fixes = json.load(fp)
    if ecosystem in fixes['ecosystems']:
        return fixes['ecosystems'][ecosystem].get(url, None)
    return url
