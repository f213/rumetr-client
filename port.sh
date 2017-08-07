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
/bin/cp dist/roometr-client-*.tar.gz /tmp/
. $dst/venv/bin/activate
echo Y|pip uninstall roometr-client
cd /tmp
/usr/bin/tar zxpvf roometr-client-*.tar.gz
cd roometr-client-*
easy_install .

cd $d
