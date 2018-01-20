# Catalog API

[![Build Status](https://travis-ci.org/awesomedata/catalog.svg?branch=master)](https://travis-ci.org/awesomedata/catalog)

A data catalog service for awesome data.

# Screenshots

[![Screenshot](https://raw.githubusercontent.com/awesomedata/catalog/master/docs/screenshots/swagger-api.png)](https://github.com/awesomedata/catalog)

# Run

Python 3.5+

* Prepare database

```bash
CREATE DATABASE IF NOT EXISTS catalogdb DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
```

* List integrated commands:

```bash
invoke --list
```

* Start app with shortcut:

```bash
export CATALOG_CONFIG=development
export SQLALCHEMY_DATABASE_URI="mysql://root:password@localhost:3306/catalogdb?charset=utf8"

invoke app.run
```

Swagger UI: `localhost:4444/api/v1`

# Reference:

* http://frictionlessdata.io

# Author

Xiaming C. <chenxm35@gmail.com>
