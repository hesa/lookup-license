#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from lookup_license.lookupurl.purl import Purl
p = Purl()

def _repo_url_helper(purl, expected):
    actual = p.repo_url(purl)

    assert actual == expected

def test_repo_url():
    PURLS = [
        
        'pkg:github/github/codeql-action/init@v2',
        'pkg:github/bcomnes/netrc-creds@v2.1.4',
        'pkg:github/nick-fields/retry@v3',
        'pkg:github/actions/setup-python@v5',
        'pkg:github/maxim-lobanov/setup-xcode@v1',
        'pkg:github/webfactory/ssh-agent@v0.8.0'
    ]
    PURLS = [
        ('pkg:github/actions/cache@v3', 'https://github.com/actions/cache/tree/v3'),
        ('pkg:github/actions/checkout@v3','https://github.com/actions/checkout/tree/v3'),
    ]

    for purl, expected in PURLS:
        _repo_url_helper(purl, expected)
