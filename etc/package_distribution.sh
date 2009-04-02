#!/bin/bash
# Script to package up the library for distribution, all pretty like

svn export . opensocial-python-client
rm -rf opensocial-python-client/etc

zip -r opensocial-python-client-`date "+%Y%m%d"`.zip opensocial-python-client
tar -cjvf opensocial-python-client-`date "+%Y%m%d"`.tar.bz opensocial-python-client
tar  -czf opensocial-python-client-`date "+%Y%m%d"`.tar.gz opensocial-python-client

rm -r opensocial-python-client
