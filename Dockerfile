########################################################################
## Author: Sean Landry
########################################################################

FROM fedora:latest

## Set the file maintainer (your name - the file's author)
LABEL maintainer "Sean Landry"


RUN mkdir /dmwrapcli

COPY . /dmwrapcli/

RUN curl -L https://github.com/docker/machine/releases/download/v0.12.2/docker-machine-`uname -s`-`uname -m` >/tmp/docker-machine && \
    chmod +x /tmp/docker-machine && \
    cp /tmp/docker-machine /usr/local/bin/docker-machine

RUN dnf install -y python3-docopt python3-yaml


