#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

#from lookup_license.lookuplicense import LookupLicense
#ll = LookupLicense()

from lookup_license.lookupurl.gitrepo import GitRepo
gitrepo = GitRepo()

def test_repos():
    REPOS = ['github.com/hesa/lookup-license/tree/main',
             'github.com/hesa/lookup-license/tree/0.1.17',
             'github.com/hesa/lookup-license/tree/hesa-fix-readme',

             'gitlab.com/hermine-project/hermine',
             'gitlab.com/hermine-project/hermine/-/tree/v0.5.1?ref_type=tags',
             'gitlab.com/hermine-project/hermine/-/tree/nico/docs?ref_type=heads',

             'cgit.freedesktop.org/cairo',
             'cgit.freedesktop.org/cairo/tree',
             'cgit.freedesktop.org/cairo/tree/?h=1.10',
             'cgit.freedesktop.org/cairo/tag/?h=1.18.4'
             ]
    for repo in REPOS:
        for pre in [ '', 'https://']:
            for post in [ '', '/', '//']:
                #url = f'{pre}{repo}{post}'
                #assert gitrepo.is_repo(url)
                #assert not gitrepo.is_file(url)
                pass

def test_files():
    FILES = [
        'github.com/aboutcode-org/scancode-toolkit/blob/develop/apache-2.0.LICENSE',
        'raw.githubusercontent.com/aboutcode-org/scancode-toolkit/develop/apache-2.0.LICENSE',
        'github.com/aboutcode-org/scancode-toolkit/blob/v32.3.2/apache-2.0.LICENSE',
        'raw.githubusercontent.com/aboutcode-org/scancode-toolkit/refs/tags/v32.3.2/apache-2.0.LICENSE',

        'gitlab.com/hermine-project/hermine/-/blob/main/LICENSE.txt?ref_type=heads',
        'gitlab.com/hermine-project/hermine/-/raw/main/LICENSE.txt?ref_type=heads',
        'gitlab.com/hermine-project/hermine/-/blob/nico/docs/LICENSE.txt?ref_type=heads',
        'gitlab.com/hermine-project/hermine/-/raw/nico/docs/LICENSE.txt?ref_type=heads',
        'gitlab.com/hermine-project/hermine/-/blob/v0.5.1/LICENSE.txt?ref_type=tags',
        'gitlab.com/hermine-project/hermine/-/raw/v0.5.1/LICENSE.txt?ref_type=tags',
        
        'cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1',
        'cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.18.4',
        'cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.10'
             ]
    for f in FILES:
        for pre in [ '', 'https://']:
            url = f'{pre}{f}'
            #import sys
            #print(f'TEST {url}')
            #assert not gitrepo.is_repo(url)
            #assert gitrepo.is_file(url)

def test_github_is_repo_fails():
    BAD_REPOS = ['github.com/aboutcode-org/scancode-toolkit/develop/',
                 'gitlab.com/hermine-project/hermine/-',
                 'gitlab.com/hermine-project/hermine/-/tree'
                 ]

    for bad_repo in BAD_REPOS:
        for pre in [ '', 'https://']:
            for post in [ '', '/', '//']:
                url = f'{pre}{bad_repo}{post}'
                #with pytest.raises(Exception):
                    #gitrepo.is_repo(url)
                    #pass

def _assert_urls(orig_url, expected_url):
    # plain url -> raw
    raw_url = gitrepo.raw_content_url(orig_url)
    import sys
    print("AU orig: " + orig_url, file=sys.stderr)
    print("AU raw : " + raw_url, file=sys.stderr)
    print("AU expe: " + expected_url, file=sys.stderr)
    assert raw_url == expected_url

    # raw url -> raw (so, should be the same)
    raw_url2 = gitrepo.raw_content_url(raw_url)
    assert raw_url2 == expected_url

def test_raw_content_url():
    LICENSE_URLS = [
        ('github.com/aboutcode-org/scancode-toolkit/blob/develop/apache-2.0.LICENSE',
         'https://raw.githubusercontent.com/aboutcode-org/scancode-toolkit/develop/apache-2.0.LICENSE'),
        ('github.com/hesa/lookup-license/blob/hesa-fix-name/LICENSE',
         'https://raw.githubusercontent.com/hesa/lookup-license/hesa-fix-name/LICENSE'
         ),
        ('github.com/hesa/lookup-license/blob/0.1.17/LICENSE',
         'https://raw.githubusercontent.com/hesa/lookup-license/0.1.17/LICENSE'
         ),
        
        ('gitlab.com/hermine-project/hermine/-/blob/main/LICENSE.txt?ref_type=heads',
        'https://gitlab.com/hermine-project/hermine/-/raw/main/LICENSE.txt?ref_type=heads'
         ),
        ('gitlab.com/hermine-project/hermine/-/blob/nico/docs/LICENSE.txt?ref_type=heads',
         'https://gitlab.com/hermine-project/hermine/-/raw/nico/docs/LICENSE.txt?ref_type=heads'
         ),
        ('gitlab.com/hermine-project/hermine/-/blob/v0.5.1/LICENSE.txt?ref_type=tags',
         'https://gitlab.com/hermine-project/hermine/-/raw/v0.5.1/LICENSE.txt?ref_type=tags'
         ),
        
        ('cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1',
         'https://cgit.freedesktop.org/cairo/plain/COPYING-LGPL-2.1'
         ),
        ('cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.0',
         'https://cgit.freedesktop.org/cairo/plain/COPYING-LGPL-2.1?h=1.0'
         ),
        ('cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.18.4',
         'https://cgit.freedesktop.org/cairo/plain/COPYING-LGPL-2.1?h=1.18.4'
         )
    ]

    for actual, expected in LICENSE_URLS:
        for pre in [ '', 'https://']:
            url = f'{pre}{actual}'
            _assert_urls(url, expected)



def test_raw_content_url_bad():
    url = 'https://someweirdplace.foo'
    with pytest.raises(Exception):
        raw_url = gitrepo.raw_content_url(url)

def test_has_branch():
    BRANCH_URLS = [ 'github.com/aboutcode-org/scancode-toolkit/blob/develop/apache-2.0.LICENSE',
                    'github.com/hesa/lookup-license/blob/main/LICENSE',

                    'gitlab.com/hermine-project/hermine/-/tree/fix/noors4gpl3?ref_type=heads',
                    'gitlab.com/hermine-project/hermine/-/tree/v0.5.1?ref_type=tags',
                    
                    'cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.0',
                    'cgit.freedesktop.org/cairo/tree/COPYING-LGPL-2.1?h=1.18.4']
    for branch_url in BRANCH_URLS:
        for pre in [ '', 'https://']:
            url = f'{pre}{branch_url}'
            assert gitrepo.has_branch(url)

def test_has_not_branch():
    NON_BRANCH_URLS = [ 'https://github.com/aboutcode-org/scancode-toolkit/',
                        'https://github.com/hesa/lookup-license/',

                        'https://gitlab.com/hermine-project/hermine',

                        'https://cgit.freedesktop.org/cairo/tree/'
                       ]
    for branch_url in NON_BRANCH_URLS:
        assert not gitrepo.has_branch(branch_url) 

def OBSOLETE_test_suggestions_nobranch():
    repo = 'https://github.com/hesa/lookup-license'

    # this is a URL with no branch in it, so the list of suggestion
    # lists should be of size 3 (main, master, develop)
    
    suggestions = gitrepo.suggest_license_files(repo)
    assert len(suggestions) == 3

    assert len(suggestions[0]) == 4
    
    for suggestion in suggestions[0]:
        assert 'https' in suggestion
        assert 'raw.githubusercontent' in suggestion


def OBSOLEETE_test_github_suggestions_branch():
    repo = 'https://github.com/hesa/lookup-license/tree/hesa-fix-name'

    # this is a URL with no branch in it, so the list of suggestion
    # lists should be of size 3 (main, master, develop)
    
    suggestions = gitrepo.suggest_license_files(repo)
    assert len(suggestions) == 3

    assert len(suggestions[0]) == 4
    
    for suggestion in suggestions[0]:
        assert 'https' in suggestion
        assert 'raw.githubusercontent' in suggestion
