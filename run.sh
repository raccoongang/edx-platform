#!/bin/bash

build() {
    docker build -t test .
}

run() {
    docker run \
        -v $(pwd)/cms/envs:/edx/edxapp/cms/envs \
        -v $(pwd)/pavelib:/edx/edxapp/pavelib \
        -v $(pwd)/common:/edx/edxapp/common \
        -v $(pwd)/openedx:/edx/edxapp/openedx \
        -v $(pwd)/cms:/edx/edxapp/cms \
        -v $(pwd)/lms:/edx/edxapp/lms \
        -v $(pwd)/cms.env.json:/edx/app/edxapp/cms.env.json \
        -v $(pwd)/lms.env.json:/edx/app/edxapp/lms.env.json \
        -v $(pwd)/cms.auth.json:/edx/app/edxapp/cms.auth.json \
        -v $(pwd)/lms.auth.json:/edx/app/edxapp/lms.auth.json \
        -it test
}

$1
