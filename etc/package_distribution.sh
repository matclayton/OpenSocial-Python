#!/bin/bash
# Script to package up the library for distribution, all pretty like

svn export . opensocial-python-client
rm -rf opensocial-python-client/etc

version=`cat VERSION`
echo 'Exporting version: '$version

SEARCH=`echo "DEVELOPMENT" | sed 's,/,\\\\/,g'`
REPLACE=`echo "$version" | sed 's,/,\\\\/,g'`
cat setup.py | sed "s/$SEARCH/$REPLACE/g" > opensocial-python-client/setup.py

zip -r opensocial-python-client-$version.zip opensocial-python-client
tar -cjvf opensocial-python-client-$version.tar.bz opensocial-python-client
tar  -czf opensocial-python-client-$version.tar.gz opensocial-python-client

rm -r opensocial-python-client
