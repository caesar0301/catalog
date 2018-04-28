FROM ubuntu:16.04

MAINTAINER Xiaming Chen <chenxm35@gmail.com>

ENV CATALOG_HOME=/usr/lib/catalog
ENV CATALOG_LOG_DIR=/var/log/catalog
ENV CATALOG_TMP=/tmp/catalog
ENV CATALOG_WEBSERVER_PORT=4444

# Install dependencies
RUN apt-get install -y libmysqlclient-dev

WORKDIR $CATALOG_TMP
ADD . $CATALOG_TMP

RUN pip install -U -r $CATALOG_TMP/requirements.txt

RUN mkdir -p $CATALOG_LOG_DIR
RUN chmod -R 777 $CATALOG_LOG_DIR

RUN cd $CATALOG_TMP
RUN python setup.py install

# Install necessary files
COPY ./docker-build/scripts/ $CATALOG_HOME/scripts/
COPY ./migrations/ $CATALOG_HOME/migrations/
COPY ./docs/ $CATALOG_HOME/docs/
COPY ./tasks/ $CATALOG_HOME/tasks/
COPY ./bin/catalog $CATALOG_HOME/scripts/

# Clear temporary files
RUN rm -rf $CATALOG_TMP

# Make binaries executable and add to global PATH
RUN chmod +x $CATALOG_HOME/scripts/*
ENV PATH $PATH:$CATALOG_HOME/scripts/

EXPOSE $CATALOG_WEBSERVER_PORT
