#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# script to verify against quite a few URLs
# to reduce time in CI/CD at Github some limits are set
# * if github and python 3.10 run only one test per url type
# * if github and not python 3.10 exit 
#

DEBUG=True
LIMITED_TEST=False

if [ ! -z $GITHUB_ACTIONS ]
then
    PYTHON_3_10=$(python3 --version | grep -c 3.10)
    if [ $PYTHON_3_10 -eq 1 ]
    then
        echo "Run inside Github and with Python 3.10 so run but with limited number of tests"
        LIMITED_TEST=True
    else
        echo "Run inside Github but not Python 3.10 so exit with 0"
        exit 0
    fi
elif [ "$1" = "--limited" ]
then
    LIMITED_TEST=True
    echo "Limited test"
#else
#    echo "All tests"
fi

PYPI_PACKAGES=("pkg:pypi/boto3@1.35.99;Apache-2.0 AND License :: OSI Approved :: Apache Software License"
               "pkg:pypi/click@8.1.8;BSD-3-Clause AND License :: OSI Approved :: BSD License"
              )
SWIFT_PACKAGES=("pkg:swift/github.com/google/abseil-cpp-binary@1.2024011602.0;Apache-2.0"
                "pkg:swift/github.com/firebase/leveldb@1.22.5;BSD-3-Clause AND generic-cla"
              )
GEM_PACKAGES=("pkg:gem/google-apis-core@0.11.1;Apache-2.0"
              "pkg:gem/google-cloud-env@1.6.0;Apache-2.0 AND NOASSERTION"
              "pkg:gem/aws-sdk-s3@1.135.0;Apache-2.0 AND NOASSERTION"
              "pkg:gem/google-cloud-env@2.3.0;Apache-2.0 AND LicenseRef-scancode-generic-cla"
              )

URLS=("https://github.com/postmodern/digest-crc/blob/main/LICENSE.txt;MIT"
      "https://raw.githubusercontent.com/postmodern/digest-crc/main/LICENSE.txt;MIT"
     )

URLS_TEXT=("https://raw.githubusercontent.com/postmodern/digest-crc/main/LICENSE.txt;MIT"
     )


verbose()
{
    echo "$*" 1>&2
}

debug()
{
    if [ "$DEBUG" = "True" ]
    then
        verbose "$*"
    fi
}

exec_ll()
{
    ./devel/lookup-license $*
#echo    ./devel/lookup-license $* >> /tmp/cli.txt
}

compare_exit()
{
    ACTUAL="$1"
    EXPECTED="$2"
    ARGS="$3"

    if [ "$ACTUAL" = "$EXPECTED" ]
    then
        return
    fi

    verbose "ERROR"
    verbose ""
    verbose " * arguments: $ARGS"
    verbose " * actual:    $ACTUAL"
    verbose " * expected:  $EXPECTED"
    exit 1
}

git_license_sub()
{
    local URL="$1"
    local EXPECTED_LICENSE="$2"
    local ARGS="$3"

    printf " * %-75s" "$URL: "
    LICENSE="$(exec_ll $ARGS "$URL" 2>/dev/null | tail -1)"
    SIMPLIFIED="$(flame simplify "$LICENSE")"
    compare_exit "$SIMPLIFIED"  "$EXPECTED_LICENSE" "$URL"
    echo OK
}


url_license_multi()
{
    local URL="$1"
    local EXPECTED_LICENSE="$2"
    local ARGS="$3"

    for post in "" "/"
    do
        for pre in "" "https://"
        do
            git_license_sub "${pre}${URL}${post}" "$EXPECTED_LICENSE" "$ARGS"
        done

        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi
    done
}

url_license()
{
    local URL="$1"
    local EXPECTED_LICENSE="$2"
    local ARGS="$3"

    git_license_sub "${URL}" "$EXPECTED_LICENSE" "$ARGS"
}

test_git_repo_licenses()
{
    echo "Check git repositories"

    # github
    url_license_multi "github.com/webfactory/ssh-agent/tree/v0.8.0" "MIT" " --gitrepo "
    if [ "$LIMITED_TEST" = "True" ]
    then
        echo
        return
    fi
    url_license_multi "github.com/webfactory/ssh-agent"             "MIT" " --gitrepo "
    echo
}

test_purl_swift_licenses()
{
    echo "Check Purls - Swift"

    # purl / pypi
    for i in ${!SWIFT_PACKAGES[@]}
    do
        swift_value=${SWIFT_PACKAGES[$i]}
        local URL="$(echo $swift_value | cut -d ";" -f 1)"
        local LIC="$(echo $swift_value | cut -d ";" -f 2)"

        # only use "--purl" if it url begins with "pkg:"
        if [ $(echo $URL | grep -c "^pkg:") -ne 0 ]
        then
            url_license "$URL"    "$LIC" " --purl "
        fi
        
        local PKG="$(basename $URL | sed 's,:,,g')"
        url_license "$PKG"    "$LIC" " --swift "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi

    done
    echo
}


test_purl_gem_licenses()
{
    echo "Check Purls - Gem"

    # purl / gem
    for i in ${!GEM_PACKAGES[@]}
    do
        gem_value=${GEM_PACKAGES[$i]}
        local URL="$(echo $gem_value | cut -d ";" -f 1)"
        local LIC="$(echo $gem_value | cut -d ";" -f 2)"

        # only use "--purl" if it url begins with "pkg:"
        if [ $(echo $URL | grep -c "^pkg:") -ne 0 ]
        then
            url_license "$URL"    "$LIC" " --purl "
        fi
        
        local PKG="$(echo $URL | sed 's,pkg:[a-z]*/,,g')"
        url_license "$PKG"    "$LIC" " --gem "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi

        local PKG="https://rubygems.org/gems/$(echo $PKG | sed 's,@,/versions/,')"
        url_license "$PKG"    "$LIC" " --gem "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi
        
    done

    echo
}


test_purl_pypi_licenses()
{
    echo "Check Purls - Pypi"

    # purl / pypi
    for i in ${!PYPI_PACKAGES[@]}
    do
        pypi_value=${PYPI_PACKAGES[$i]}
        local URL="$(echo $pypi_value | cut -d ";" -f 1)"
        local LIC="$(echo $pypi_value | cut -d ";" -f 2)"

        # only use "--purl" if it url begins with "pkg:"
        if [ $(echo $URL | grep -c "^pkg:") -ne 0 ]
        then
            url_license "$URL"    "$LIC" " --purl "
        fi
        
        local PKG="$(echo $URL | sed 's,pkg:[a-z]*/,,g')"
        url_license "$PKG"    "$LIC" " --pypi "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi

        local PKG="https://pypi.org/project/$(echo $PKG | sed 's,@,/,')"
        url_license "$PKG"    "$LIC" " --pypi "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi
    done

 #   "pkg:pypi/click@8.1.8" "BSD-3-Clause" " --purl "
    echo
}


test_license_url()
{
    local URL="$1"
    local EXP="$2"
    local LICENSE=$(exec_ll --url $URL)
    compare_exit "$LICENSE" "$EXP" "$URL"
}
    
test_license_urls()
{
    echo "Check Url"

    # url
    for i in ${!URLS[@]}
    do
        url_value=${URLS[$i]}
        local URL="$(echo $url_value | cut -d ";" -f 1)"
        local LIC="$(echo $url_value | cut -d ";" -f 2)"
        url_license "$URL"    "$LIC" " --url "
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi
    done
    echo
}

test_license_texts()
{
    echo "Check text from Url"

    # url
    for i in ${!URLS_TEXT[@]}
    do
        url_value=${URLS_TEXT[$i]}
        local URL="$(echo $url_value | cut -d ";" -f 1)"
        local LIC="$(echo $url_value | cut -d ";" -f 2)"
        printf " * %-75s" "text from $URL: "
        LICENSE_TEXT="$(curl -s -LJ "$URL")"
        ACTUAL=$(echo "$LICENSE_TEXT" | exec_ll "$URL"    "$LICENSE_TEXT" "")
        
        compare_exit "$ACTUAL" "$LIC" ""
        echo OK
        if [ "$LIMITED_TEST" = "True" ]
        then
            break
        fi
    done
    echo
}

test_purl_pypi_licenses
test_purl_swift_licenses
test_purl_gem_licenses
test_license_urls
test_license_texts
test_git_repo_licenses
