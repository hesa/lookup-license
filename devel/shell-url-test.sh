#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail

LICENSE_URL="https://github.com/hesa/foss-licenses/blob/main/LICENSES/GPL-3.0-or-later.txt"

output_session()
{
    echo url
    echo "${LICENSE_URL}"
    echo url
    echo "${LICENSE_URL}"
}

output_session | PYTHONPATH=. python3 ./lookup_license/__main__.py --shell
RET=$?
echo
exit $RET
