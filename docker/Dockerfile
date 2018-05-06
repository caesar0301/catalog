FROM caesar0301/catalog_builder:latest

MAINTAINER Xiaming Chen <chenxm35@gmail.com>

ENV CATALOG_HOME=/usr/lib/catalog
ENV CATALOG_LOG_DIR=/var/log/catalog
ENV CATALOG_TMP=/tmp/catalog
ENV CATALOG_WEBSERVER_PORT=4444

# Install dependencies
RUN apt-get update
RUN apt-get install -y libmysqlclient-dev python-pip

WORKDIR $CATALOG_HOME

# Fetch latest source code
RUN cd /tmp && rm -rf catalog \
    && git clone http://github.com/awesomedata/catalog.git

RUN cd $CATALOG_TMP
RUN pwd && ls && pip install -U -r requirements.txt
RUN python setup.py install
RUN cp -r docker/scripts $CATALOG_HOME/scripts
RUN cp -r migrations $CATALOG_HOME/migrations
RUN cp -r docs $CATALOG_HOME/docs
RUN cp -r tasks $CATALOG_HOME/tasks
RUN cp -r bin/catalog $CATALOG_HOME/scripts/

# Clear temporary files
RUN rm -rf $CATALOG_TMP

# Logging file directory
RUN mkdir -p $CATALOG_LOG_DIR
RUN chmod -R 777 $CATALOG_LOG_DIR

# Make binaries executable and add to global PATH
RUN chmod +x $CATALOG_HOME/scripts/*
ENV PATH $PATH:$CATALOG_HOME/scripts/

EXPOSE $CATALOG_WEBSERVER_PORT
