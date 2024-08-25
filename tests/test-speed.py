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


def license_file(ll, license_file):
    start = time.time()
    result = ll.lookup_license_file(license_file)
    end = time.time()
    elapsed = (end-start) * 10**3
    return result, elapsed

def license_text(ll, text):
    start = time.time()
    result = ll.lookup_license_text(text)
    end = time.time()
    elapsed = (end-start) * 10**3
    return result, elapsed


LICENSES = [
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "mit",
    "This is the first released version of the Lesser GPL.  It also counts as the successor of the GNU Library Public License, version 2, hence the version number 2.1.",
    "This is text that does not contain any real license data ... just mumbo jumbo really. And more stupid stuff",
    "BSD",
    "X11",
    "nada"
]

def __assert_with_info(lic, res, elapsed, max_time, i):
    if elapsed > max_time:
        print("* license  " + (str(lic)))
        print("* res      " + (str(res)))
        print("* elapsed  " + (str(elapsed)))
        print("* max time " + (str(max_time)))
        print("* i        " + (str(i)))
        assert elapsed < max_time # milli seconds
    

def main():
    ll = LookupLicense()

    print("Short license:")
    # first short
    res, elapsed = license_text(ll, "GPLv3+")
    print(" * first:      " + str(elapsed))
    assert res['normalized'][0] == "GPL-3.0-or-later"
    assert elapsed < 1000 # one second
    
    # first short
    res, elapsed = license_text(ll, "GPLv3+")
    print(" * second:     " + str(elapsed))
    assert res['normalized'][0] == "GPL-3.0-or-later"
    assert elapsed < 1 # milli seconds
    
    print("Long license:")
    # first long text
    res, elapsed = license_file(ll, "LICENSES/GPL-3.0-or-later.txt")
    assert res['normalized'][0] == "GPL-3.0-only"
    print(" * first:      " + str(elapsed))
    assert elapsed < 3000 # milli seconds
    
    # second long text
    res, elapsed = license_file(ll, "LICENSES/GPL-3.0-or-later.txt")
    assert res['normalized'][0] == "GPL-3.0-only"
    print(" * second:     " + str(elapsed))
    assert elapsed < 1 # milli seconds

    max_time = 200
    elapsed_short = []
    elapsed_long = []
    for i in range(0,1000):
        # short license texts
        for lic in LICENSES:
            res, elapsed = license_text(ll, lic)
            __assert_with_info(lic, res, elapsed, max_time, i)
            elapsed_short.append(elapsed)
            #print("* elapsed  " + (str(elapsed)))

        # long license texts
        for f in glob.glob('tests/licenses/*.LICENSE'):
            res, elapsed = license_text(ll, lic)
            __assert_with_info(lic, res, elapsed, max_time, i)
            elapsed_long.append(elapsed)
            #print("* elapsed  " + (str(elapsed)))
            
        # the coming lookups should be quick, so lower max_time
        max_time = 1

    print()
    print(f'Short average: {sum(elapsed_short)/len(elapsed_short)}, based on {len(elapsed_short)} values')
    print(f'Long average:  {sum(elapsed_long)/len(elapsed_long)}, based on {len(elapsed_long)} values')
    
    
if __name__ == '__main__':
    main()
