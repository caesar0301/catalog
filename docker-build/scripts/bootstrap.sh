#!/bin/bash
set -e

echo "options use-vc" >> /etc/resolv.conf

FILEPATH=$(cd ${0%/*} && echo $PWD/${0##*/})
THISFOLDER=$(cd $(dirname $FILEPATH) && pwd)

[ -f $THISFOLDER/env.sh ] && {
  . $THISFOLDER/env.sh
}

cd $OCKLE_HOME

OCKLE_CMD=`which ockle`
if [ $? -ne 0 ]; then
    echo "Executable binary 'ockle' not in the PATH, exit."
    exit 1
else
    echo "Found Ockle binary $OCKLE_CMD"
fi

echo "Create database if not exists ..."
mysql -u ${OCKLE_MYSQL_USERNAME} \
    --password=${OCKLE_MYSQL_PASSWORD} \
    -h ${OCKLE_MYSQL_SERVER} \
    -P ${OCKLE_MYSQL_PORT} \
    -f << EOF
CREATE DATABASE IF NOT EXISTS ${OCKLE_DATABASE} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
EOF

# Initialize schema with migrated versions
$OCKLE_CMD db upgrade

# Initialize or upgrade products
$OCKLE_CMD initdb -p $PRODUCT_META_HOME

$OCKLE_CMD runserver
