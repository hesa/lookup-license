#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

LL_TMP_DIR=/tmp/ll-tmp
ACTUAL_OUTPUT=${LL_TMP_DIR}/actual-output.txt
EXPECTED_OUTPUT=${LL_TMP_DIR}/expected-output.txt
LOOKUP_TMP_FILE=${LL_TMP_DIR}//lookups.tmp
mkdir -p ${LL_TMP_DIR}
rm -f ${EXPECTED_OUTPUT} ${LOOKUP_TMP_FILE} ${ACTUAL_OUTPUT}

LOOPS=10
if [ "$1" != "" ]
then
    LOOPS=$1
fi

DEL_STR=""
for i in $(seq 1 50)
do
    DEL_STR="\b$STR"
done
DEL_STR="$STR\r"

# License names to loop over
LICENSES="AFL-1.1  AFL-1.2 AFL-2.0 AFL-2.1 AFL-3.0 Apache-1.0 Apache-1.1 Apache-2.0 APSL-2.0 Artistic-1.0 Artistic-2.0 Autoconf-exception-2.0 Autoconf-exception-3.0 Beerware Bitstream-Vera BlueOak-1.0.0 Bootloader-exception BSD-1-Clause BSD-2-Clause BSD-2-Clause-Patent BSD-2-Clause-Views BSD-3-Clause-Clear BSD-3-Clause BSD-3-Clause-No-Nuclear-Warranty BSD-4-Clause BSD-4-Clause-UC BSD-Source-Code BSL-1.0 CC0-1.0 CC-BY-3.0 CC-BY-4.0 CC-BY-SA-2.5 CC-BY-SA-3.0 CC-BY-SA-4.0 CC-PDDC CDDL-1.0 CDDL-1.1 Classpath-exception-2.0 CPL-1.0 ECL-1.0 EFL-1.0 EFL-2.0 EPL-1.0 EPL-2.0 EUPL-1.0 EUPL-1.1 EUPL-1.2 GCC-exception-3.1 GPL-1.0-only  GPL-2.0-only GPL-3.0-only HPND IJG IJG-short ISC JSON Latex2e LGPL-3.0-only Libpng Libtool-exception LicenseRef-scancode-boost-original LicenseRef-scancode-docbook  LicenseRef-scancode-indiana-extreme LicenseRef-scancode-wtfpl-1.0 LicenseRef-scancode-xfree86-1.0 LicenseRef-scancode-zpl-1.0 Linux-syscall-note LLVM-exception MIT-0 MIT-advertising MIT MIT-Modern-Variant MITNFA MIT-Wu MPL-1.0 MPL-1.1 NAIST-2003 NCSA OCaml-LGPL-linking-exception ODC-By-1.0 OFL-1.0 OFL-1.1 PostgreSQL Python-2.0.1 RSA-MD SAX-PD Sendmail SGI-B-2.0 Sleepycat  SSPL-1.0 SWL TCL Unlicense Vim W3C-19980720 W3C-20150513 W3C WTFPL X11-distribute-modifications-variant Xfig XFree86-1.1 Zlib ZPL-1.1 ZPL-2.0 ZPL-2.1 AGPL-3.0-only"

#
# prepare a text command interaction for a license
#
format_license_text()
{
    echo "text";
    cat tests/licenses/${1}.LICENSE
    echo
    echo ENDOFLICENSETEXT 
}

#
# prepare a file command interaction for a license file
#
format_license_file()
{
    echo "file"
    echo tests/licenses/${1}.LICENSE
}

#
# create a LookupLicense response for a license (for checking the actual response)
#
expected_license()
{
    echo "['${1}']"
}

#
# output to stderr, no newline
#
errn()
{
    echo -n "$*" 1>&2
}

#
# output to stderr, clean line first, no newlines
#
rerrn()
{
    echo -n -e "${DEL_STR}$*" 1>&2
}

#
# output to stderr
#
err()
{
    echo "$*" 1>&2
}

#
# loop over licenses and license files, create interactive commands 
#
loop_licenses()
{
    CNT=0
    for i in $(seq 1 $LOOPS)
    do
        for lic in  $LICENSES ;
        do
            # Test text input
            rerrn $lic
            format_license_text $lic
            #echo "#$lic"  >> ${EXPECTED_OUTPUT}
            expected_license $lic >> ${EXPECTED_OUTPUT}
            #err " OK"
            CNT=$(( $CNT + 1 ))
            #err "$CNT"

            # Test file (name) input
            #errn $lic
            format_license_file $lic
            #echo "#$lic"  >> ${EXPECTED_OUTPUT}
            expected_license $lic >> ${EXPECTED_OUTPUT}
            #err " OK"
            CNT=$(( $CNT + 1 ))
            #err "$CNT"
            #errn "."
        done
    done
    rerrn ""
    return $CNT
}

# store interactive command in tmp file
START=$(date "+%s%N")
loop_licenses > ${LOOKUP_TMP_FILE}
STOP=$(date "+%s%N")
ELAPSED=$( echo "scale=1; ( $STOP - $START ) / 1000000000" | bc -l)
err "Finished creating $CNT commands in $ELAPSED seconds"


# pipe commands through shell and strip information for later check (diff)
START=$(date "+%s%N")


cat ${LOOKUP_TMP_FILE} | \
    PYTHONPATH=. ./lookup_license/__main__.py  --shell | \
    grep -v -e ENDOFLICENSETEXT -e Welcome -e \"^$\" | \
    grep -v "^>>> Enter" | \
    grep ">>> \[" | \
    sed 's,>>> ,,g' \
        > ${ACTUAL_OUTPUT}
#cat ${LOOKUP_TMP_FILE} | PYTHONPATH=. ./lookup_license/__main__.py  --shell | grep -v -e "ENDOFLICENSETEXT" -e Welcome -e "^$"  | sed 's,LookupLicense> ,,g' | grep "^\["  > ${ACTUAL_OUTPUT}




#
STOP=$(date "+%s%N")
err "$CNT lookups"
#

# Check expected vs actual response
diff $ACTUAL_OUTPUT $EXPECTED_OUTPUT 
RET=$?
if [ $RET -eq 0 ]
then
    RESULT_STRING="OK"
else
    RESULT_STRING="Fail"
    echo "diff between  $ACTUAL_OUTPUT $EXPECTED_OUTPUT "
fi
err "Diff: $RESULT_STRING"
ELAPSED=$(( $STOP - $START ))
err "Time: $(( $ELAPSED / 1000000)) ms"
AVG=$(echo "scale=3; $ELAPSED / $CNT / 1000000" | bc -l)
err "Average: $AVG ms"
exit $RET
