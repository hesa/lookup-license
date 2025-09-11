#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookupurl.pypi import Pypi
from lookup_license.lookupurl.gem import Gem
from lookup_license.lookupurl.swift import Swift
from lookup_license.lookupurl.clearlydefined import ClearlyDefined

cd = ClearlyDefined()

#
# pypi
#
def test_get_parameters_pypi_package():
    # from pypi package to parameters
    pp = Pypi()
    params = pp.get_parameters('boto3@1.35.99', None)
    assert 'pypi' == params.get('namespace')
    assert 'boto3' == params.get('name')
    assert '1.35.99' == params.get('version')

def test_get_parameters_pypi_https():
    # from https package to parameters
    pp = Pypi()
    params = pp.get_parameters('https://pypi.org/project/boto3/1.35.99', None)
    assert 'pypi' == params.get('namespace')
    assert 'boto3' == params.get('name')
    assert '1.35.99' == params.get('version')

def test_get_parameters_pypi_package_no_version():
    # from pypi package to parameters
    pp = Pypi()
    params = pp.get_parameters('boto3', '1.35.99')
    assert 'pypi' == params.get('namespace')
    assert 'boto3' == params.get('name')
    assert '1.35.99' == params.get('version')

def test_get_parameters_pypi_purl():
    # from purl package to parameters
    pp = Pypi()
    params = pp.get_parameters('pkg:pypi/pypi/boto3@1.35.99', None)
    assert 'pypi' == params.get('namespace')
    assert 'boto3' == params.get('name')
    assert '1.35.99' == params.get('version')

    
#
# Gem
#
def test_get_parameters_gem_package():
    # from gem package to parameters
    g = Gem()
    params = g.get_parameters('google-apis-core@0.11.1', None)
    assert 'gem' == params.get('namespace')
    assert 'google-apis-core' == params.get('name')
    assert '0.11.1' == params.get('version')

def test_get_parameters_gem_https():
    # from gem package to parameters
    g = Gem()
    params = g.get_parameters('https://rubygems.org/gems/google-apis-core@0.11.1', None)
    assert 'gem' == params.get('namespace')
    assert 'google-apis-core' == params.get('name')
    assert '0.11.1' == params.get('version')

def test_get_parameters_gem_package_no_version():
    # from gem package to parameters
    g = Gem()
    params = g.get_parameters('google-apis-core', '0.11.1')
    print("param " + str(params))
    assert 'gem' == params.get('namespace')
    assert 'google-apis-core' == params.get('name')
    assert '0.11.1' == params.get('version')

def test_get_parameters_gem_purl():
    # from purl package to parameters
    g = Gem()
    params = g.get_parameters('pkg:gem/google-apis-core@0.11.1', None)
    assert 'gem' == params.get('namespace')
    assert 'google-apis-core' == params.get('name')
    assert '0.11.1' == params.get('version')

#
# Swift
#
def test_get_parameters_swift_package():
    # from swift package to parameters
    s = Swift()
    params = s.get_parameters('abseil-cpp-binary@1.2024011602.0', None)
    assert 'swift' == params.get('namespace')
    assert 'abseil-cpp-binary' == params.get('name')
    assert '1.2024011602.0' == params.get('version')

def test_get_parameters_swift_package_no_version():
    # from swift package to parameters
    s = Swift()
    params = s.get_parameters('abseil-cpp-binary', '1.2024011602.0')
    print("param " + str(params))
    assert 'swift' == params.get('namespace')
    assert 'abseil-cpp-binary' == params.get('name')
    assert '1.2024011602.0' == params.get('version')

def test_get_parameters_swift_purl():
    # from purl package to parameters
    s = Swift()
    params = s.get_parameters('pkg:swift/rubygems/github.com/google/abseil-cpp-binary@1.2024011602.0', None)
    
    assert 'rubygems/github.com/google' == params.get('namespace')
    assert 'abseil-cpp-binary' == params.get('name')
    assert '1.2024011602.0' == params.get('version')


