#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

ll()
{
    PYTHONPATH=. python3 ./lookup_license/__main__.py $*
}

exit_on_failure()
{
    if [ $1 -ne 0 ]
    then
        exit $1
    fi
}

inform()
{
    echo
    echo $*
}

inform "# Test arguments --help"
ll --help > /dev/null
exit_on_failure $?

inform "# Test no arguments, and \"mit\" from stdin"
echo "mit" | ll
exit_on_failure $?

inform "# Test argument \"mit\""
ll "mit"
exit_on_failure $?

inform "# Test arguments \"mit and bsd3\""
ll "mit and bsd3"
exit_on_failure $?

inform "# Test arguments mit and bsd3"
ll mit and bsd3
exit_on_failure $?

inform "# Test arguments --file LICENSES/GPL-3.0-or-later.txt"
ll --file LICENSES/GPL-3.0-or-later.txt
exit_on_failure $?
