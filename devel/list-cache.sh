#!/bin/bash


CACHE_DB=~/.ll/cache.db

sql_e()
{
    echo "$*" | sqlite3 $CACHE_DB
}

echo "Tables:"
echo "-------"
sql_e .tables
echo

echo "Columns:"
echo "-------"
sql_e .schema Cache | head -1
echo

echo "Rows:"
echo "-------"
sql_e SELECT store_time, key FROM Cache 
echo


