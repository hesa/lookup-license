#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookupurl.clearlydefined import ClearlyDefined

cd = ClearlyDefined()

def test_parameters_pypi():
    coord_url = cd.parameters_to_url('pypi/pypi', None, 'boto3', '1.35.99')
    assert 'https://api.clearlydefined.io/definitions/pypi/pypi/-/boto3/1.35.99' == coord_url

def test_parameters_gem():
    coord_url = cd.parameters_to_url('gem/rubygems', None, 'google-apis-core', '0.11.1')
    assert 'https://api.clearlydefined.io/definitions/gem/rubygems/-/google-apis-core/0.11.1' == coord_url

def test_parameters_maven():
    coord_url = cd.parameters_to_url('maven', 'mavencentral', 'org.apache.httpcomponents/httpcore', '4.3')
    assert 'https://api.clearlydefined.io/definitions/maven/mavencentral/org.apache.httpcomponents/httpcore/4.3' == coord_url
   
