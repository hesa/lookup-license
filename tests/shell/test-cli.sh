#!/bin/bash

DEBUG=True

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
    verbose " * arguments: $ARGS"
    verbose " * actual:    $ACTUAL"
    verbose " * expected:  $EXPECTED"
    
}

git_repo_license_sub()
{
    local URL="$1"
    local EXPECTED_LICENSE="$2"

    printf " * %-75s" "$URL: "
    LICENSE=$(exec_ll --gitrepo "$URL" 2>/dev/null | tail -1)
    
    compare_exit "$LICENSE"  "$EXPECTED_LICENSE" "$URL"
    echo OK
}


git_repo_license()
{
    local URL="$1"
    local EXPECTED_LICENSE="$2"

    for post in "" "/"
    do
        for pre in "" "https://"
        do
            git_repo_license_sub "${pre}${URL}${post}" "$EXPECTED_LICENSE"
        done
    done
}

test_git_repo_licenses()
{
    echo "Check git repositories"
    git_repo_license "github.com/webfactory/ssh-agent/tree/v0.8.0" "MIT"
    git_repo_license "github.com/webfactory/ssh-agent"             "MIT"
}

test_git_repo_licenses
