#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

LICENSES="BSD-1-Clause BSD-2-Clause BSD-2-Clause-Patent BSD-2-Clause-Views BSD-3-Clause-Clear BSD-3-Clause HPND  MIT MPL-2.0 AGPL-3.0-only"

LL_TMP_DIR=/tmp/ll-tmp
mkdir -p ${LL_TMP_DIR}

MULT_FILE=${LL_TMP_DIR}/multiple-licenses.txt
EXP_FILE=${LL_TMP_DIR}/expected.txt
ACT_FILE=${LL_TMP_DIR}/actual.txt
rm -f $MULT_FILE $EXP_FILE $ACT_FILE

for lic in $LICENSES
do
    cat tests/licenses/${lic}.LICENSE
    echo
    echo $lic >> ${EXP_FILE}
done > ${MULT_FILE}

mv ${EXP_FILE} ${EXP_FILE}.tmp
sort ${EXP_FILE}.tmp > ${EXP_FILE}

(echo "file"; echo "${MULT_FILE}" ) | PYTHONPATH=. ./lookup_license/__main__.py  --shell \
    | grep -v -e "ENDOFLICENSETEXT" -e Welcome -e "^$" -e "Enter"  \
    | sed 's,LookupLicense> ,,g' \
    | grep -v "^[ \t]*$" \
    | grep -v '>>>[ ]*$' \
    | sed -e 's,>>>,,g' \
    | sed -e "s,',,g" -e "s,\[,,g"  -e "s,],,g" -e 's,[ ]*,,g' \
    | tr "," "\n" \
    | sort > $ACT_FILE

diff $EXP_FILE $ACT_FILE
RET=$?
if [ $RET -eq 0 ]
then
    RESULT_STRING="OK"
else
    RESULT_STRING="Fail"
    echo "Diff found between:"
    echo $EXP_FILE
    echo $ACT_FILE
    echo "To reproduce: "
    echo "(echo \"file\"; echo \"${MULT_FILE}\" ) | \\"
    echo  "  PYTHONPATH=. ./lookup_license/__main__.py  --shell | \\"
    echo "   grep -v -e \"ENDOFLICENSETEXT\" -e Welcome -e \"^$\" -e \"Enter\" | \\"
    echo "   sed 's,LookupLicense> ,,g' | \\"
    echo "   grep -v \"^$\"  | \\"
    echo "   grep -v '>>>[ ]*$' | \\"
    echo "   sed -e 's,>>>,,g' | \\"
    echo "   sed -e \"s,',,g\" -e \"s,\[,,g\"  -e \"s,],,g\" -e 's,[ ]*,,g' | \\"
    echo "   tr \",\" \"\n\" | \\"
    echo "   sort\""
    
fi
echo Diff: $RESULT_STRING
exit $RET
