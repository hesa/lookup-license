#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest
import requests

from lookup_license.lookupurl.go import Go
from lookup_license.lookuplicense import LookupLicense


go = Go()
ll = LookupLicense()

def test_homepage_url():
    from lookup_license.retrieve import Retriever
    with open ('tests/input/yaml@v1.4.0') as fp:
        repo_url = go.homepage_repo_url(fp.readlines())
        assert repo_url == 'https://github.com/kubernetes-sigs/yaml'

def test_homepage_license_files():
    from lookup_license.retrieve import Retriever
    with open ('tests/input/yaml@v1.4.0?tab=licenses') as fp:
        files = go.homepage_license_files(fp.readlines())
        assert files == ['sigs.k8s.io/yaml@v1.4.0/LICENSE']

def test_homepage_license_texts():
    from lookup_license.retrieve import Retriever
    with open ('tests/input/yaml@v1.4.0?tab=licenses') as fp:
        lines = fp.readlines()
        print("lines: " + str(len(lines)))
        license_texts = go.homepage_license_texts(lines)
        assert len(license_texts) == 1

        # check that the content identifies as MIT, Apache-2.0, BSD-3-Clause
        # and possibly some others
        license_text = license_texts[0]
        lookedup_license = ll.lookup_license_text(license_text)
        licenses = ', '.join([x['license'] for x in lookedup_license['normalized']])
        assert 'BSD-3-Clause' in licenses
        assert 'MIT' in licenses
        assert 'Apache-2.0' in licenses

test_homepage_url()
test_homepage_license_files()
test_homepage_license_texts()
