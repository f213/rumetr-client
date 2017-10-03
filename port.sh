#!/bin/bash
#
# Copy the current branch to the destination venv
#

d=`pwd`
dst=$1

if [ -z $dst ]; then
    echo "Usage: ${0} <destination env>"
    exit 127
fi

. venv/bin/activate
/bin/rm -Rf dist
python setup.py sdist
/bin/cp dist/rumetr-client-*.tar.gz /tmp/
. $dst/venv/bin/activate
echo Y|pip uninstall roometr-client
echo Y|pip uninstall rumetr-client
cd /tmp
/usr/bin/tar zxpvf rumetr-client-*.tar.gz
cd rumetr-client-*
easy_install .

cd $d
