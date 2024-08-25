#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import glob
import json
import logging
import sys
import time

from lookup_license.lookuplicense import LookupLicense
from flame.license_db import FossLicenses

    

def main():
    ll = LookupLicense()
    fl = FossLicenses()
    
    res = ll.lookup_license_text("BSD")
    print(json.dumps(res, indent=4))
    
    res = ll.lookup_license_text("slkj d09u aslk #/& I/# ")
    print(json.dumps(res, indent=4))
    
if __name__ == '__main__':
    main()
