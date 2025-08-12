#!/bin/bash

PURLDB_URL="https://public.purldb.io/api"
PURL="$1"

validate_purl()
{
    purl="$1"
    enc_purl=$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' "$purl")
    RET=$(curl -s -I "${PURLDB_URL}/validate/?purl=$enc_purl" | grep -c "HTTP/2 4")
    return $RET
}

lookup_purl_git()
{
    purl="$1"
    enc_purl=$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' "$purl")
    curl "${PURLDB_URL}/from_purl/purl2git/?package_url=$enc_purl" ;
}

echo "Purl"
echo "------"
echo "from packageurl import PackageURL;import json;p=PackageURL.from_string('$PURL').to_dict();print(json.dumps(p, indent=4))" | python3 
echo
echo "Git repo url via purl2url"
echo "------------------------"
echo "from packageurl.contrib import purl2url; p=purl2url.get_repo_url('$URL'); print(p)" | python3 
echo
echo "Git repo via purldb"
echo "------------------------"
validate_purl "$PURL" && lookup_purl_git "$PURL" || echo "invalid purl (\"$PURL\")"
echo
echo
