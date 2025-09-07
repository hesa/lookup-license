#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookupurl.purldb import PurlDB

pdb = PurlDB()

# pypi
def test_parameters_pypi():
    purldb_url = pdb.parameters_to_url('pypi', 'pypi', 'boto3', '1.35.99')
    assert 'https://public.purldb.io/api/collect/?purl=pkg:pypi/pypi/boto3@1.35.99' == purldb_url

# gem
def test_parameters_gem():
    purldb_url = pdb.parameters_to_url('gem', 'rubygems', 'google-apis-core', '0.11.1')
    assert 'https://public.purldb.io/api/collect/?purl=pkg:gem/rubygems/google-apis-core@0.11.1' == purldb_url

# maven
def test_parameters_maven():
    purldb_url = pdb.parameters_to_url('maven', 'mavencentral', 'google-apis-core', '0.11.1')
    assert 'https://public.purldb.io/api/collect/?purl=pkg:maven/mavencentral/google-apis-core@0.11.1' == purldb_url
