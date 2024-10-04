#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

for f in $(ls devel/*.sh | grep -v all.sh)
do
    echo "    ----==== $f ====-----"
    ./$f
    if [ $? -ne 0 ]
    then
        echo "$f failed"
        exit 1
    fi
done

echo
echo
echo
echo
echo
echo "all devel scripts passed :)"
echo
echo
echo
