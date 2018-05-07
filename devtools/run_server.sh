#!/bin/bash
export CATALOG_CONFIG=development
export SQLALCHEMY_DATABASE_URI="mysql://root:password@localhost:3306/catalogdb?charset=utf8"

invoke app.run
