#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookuplicense import LookupLicense

ll = LookupLicense()


# Lookup license text
# - shorts
def test_lookup_license_text_ambig():
    res = ll.lookup_license_text("BSD")
    assert res['normalized'] == ['BSD']

def test_lookup_license_text_good():
    res = ll.lookup_license_text("BSD-3-Clause")
    assert res['normalized'] == ['BSD-3-Clause']

def test_lookup_license_text_alias():
    res = ll.lookup_license_text("BSD3")
    assert res['normalized'] == ['BSD-3-Clause']

def test_lookup_license_text_bad():
    bad_lic = 'slkj d09u aslk #/& I/# '
    res = ll.lookup_license_text(bad_lic)
    assert res['normalized'] == []

# Lookup license text
# - long
def test_long_lookup_license_text_good():
    data = open('tests/licenses/MIT.LICENSE').read()
    res = ll.lookup_license_text(data)
    assert res['normalized'][0]['license'] == 'MIT'

def test_long_lookup_license_text_good_multiple():
    mit_data = open('tests/licenses/MIT.LICENSE').read()
    bsd3_data = open('tests/licenses/BSD-3-Clause.LICENSE').read()
    res = ll.lookup_license_text(f'{mit_data}\n{bsd3_data}')
    assert res['normalized'][0]['license'] in ['BSD-3-Clause', 'MIT']
    assert res['normalized'][1]['license'] in ['BSD-3-Clause', 'MIT']

def test_long_lookup_license_text_bad():
    bad_lic = 'something that does not look like a license...and make it long by doing times 100'*100
    res = ll.lookup_license_text(bad_lic)
    assert res['normalized'] == []

# Lookup license file
# 
def test_lookup_license_file_good():
    res = ll.lookup_license_file('tests/licenses/MIT.LICENSE')
    assert res['normalized'][0]['license'] == 'MIT'

def test_lookup_license_file_bad():
    with pytest.raises(Exception) as e_info:
        res = ll.lookup_license_file('tests/licenses/oh-no-this-does-not-exist.LICENSE')
        


# Lookup license url
# 
def test_lookup_license_url_good():
    res = ll.lookup_license_url('https://raw.githubusercontent.com/hesa/lookup-license/main/LICENSES/GPL-3.0-or-later.txt')
    assert res['normalized'][0]['license'] == 'GPL-3.0-only'

def test_lookup_license_url_html():
    res = ll.lookup_license_url('https://github.com/hesa/lookup-license/blob/main/LICENSES/GPL-3.0-or-later.txt')
    assert res['normalized'][0]['license'] == 'GPL-3.0-only'

def test_lookup_license_url_bad():
    res = ll.lookup_license_url('https://github.com/hesa/lookup-license/blob/main/LICENSES/does-not-exist.txt')
    assert res['normalized'] == None
    





