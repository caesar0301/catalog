FROM 172.16.1.99/transwarp/CATALOG_builder:tdc-1.0

MAINTAINER xiaming.chen@transwarp.io

ENV CATALOG_HOME=/usr/lib/catalog
ENV CATALOG_LOG_DIR=/var/log/catalog
ENV CATALOG_TMP=/tmp/catalog
ENV CATALOG_WEBSERVER_PORT=5180

WORKDIR $CATALOG_TMP
ADD . $CATALOG_TMP

RUN pip install -U -i http://172.16.1.161:30033/repository/pypi/simple/ \
    -r $CATALOG_TMP/requirements.txt \
    --trusted-host=172.16.1.161 \
    --timeout=120

RUN mkdir -p $CATALOG_LOG_DIR
RUN chmod -R 777 $CATALOG_LOG_DIR

RUN cd $CATALOG_TMP
RUN python setup.py install

# Install necessary files
COPY ./docker-build/scripts/ $CATALOG_HOME/scripts/
COPY ./migrations/ $CATALOG_HOME/migrations/
COPY ./bin/catalog $CATALOG_HOME/scripts/

# Clear temporary files
RUN rm -rf $CATALOG_TMP

# Make binaries executable and add to global PATH
RUN chmod +x $CATALOG_HOME/scripts/*
ENV PATH $PATH:$CATALOG_HOME/scripts/

EXPOSE $CATALOG_WEBSERVER_PORT
