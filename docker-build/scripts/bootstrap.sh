#!/bin/bash
set -e

export DEBUG=${DEBUG:-0}
export FLASK_ENV=${FLASK_ENV:-"production"}

export CATALOG_HOME=${CATALOG_HOME:-"/usr/lib/catalog"}
export CATALOG_LOG_DIR=${CATALOG_LOG_DIR:-"/var/log/catalog"}

export CATALOG_MYSQL_SERVER=${CATALOG_MYSQL_SERVER:-"localhost"}
export CATALOG_MYSQL_PORT=${CATALOG_MYSQL_PORT:-"3306"}
export CATALOG_MYSQL_USERNAME=${CATALOG_MYSQL_USERNAME:-"root"}
export CATALOG_MYSQL_PASSWORD=${CATALOG_MYSQL_PASSWORD:-"password"}
export CATALOG_DATABASE=${CATALOG_DATABASE:-"catalogdb"}
export SQLALCHEMY_DATABASE_URI=mysql://${CATALOG_MYSQL_USERNAME}:${CATALOG_MYSQL_PASSWORD}@${CATALOG_MYSQL_SERVER}:${CATALOG_MYSQL_PORT}/${CATALOG_DATABASE}?charset=utf8

echo "options use-vc" >> /etc/resolv.conf

FILEPATH=$(cd ${0%/*} && echo $PWD/${0##*/})
THISFOLDER=$(cd $(dirname $FILEPATH) && pwd)

[ -f $THISFOLDER/env.sh ] && {
  . $THISFOLDER/env.sh
}

cd $CATALOG_HOME

echo "Create database if not exists ..."
mysql -u ${CATALOG_MYSQL_USERNAME} \
    --password=${CATALOG_MYSQL_PASSWORD} \
    -h ${CATALOG_MYSQL_SERVER} \
    -P ${CATALOG_MYSQL_PORT} \
    -f << EOF
CREATE DATABASE IF NOT EXISTS ${CATALOG_DATABASE} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
EOF

invoke app.run
