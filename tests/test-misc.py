#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from lookup_license.lookuplicense import LookupLicense

def main():
    ll = LookupLicense()

    res = ll.lookup_license_text("BSD")
    print(json.dumps(res, indent=4))

    res = ll.lookup_license_text("slkj d09u aslk #/& I/# ")
    print(json.dumps(res, indent=4))


if __name__ == '__main__':
    main()
