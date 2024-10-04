#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail

output_session()
{
    echo text
    echo "mit"
    echo ENDOFLICENSETEXT
    echo file
    echo LICENSES/GPL-3.0-or-later.txt
    echo text
    echo bsd3
}

output_session | PYTHONPATH=. python3 ./lookup_license/__main__.py --shell
RET=$?
echo
exit $RET
