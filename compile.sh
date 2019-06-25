#!/bin/bash
. .node/bin/activate && \
    paver install_node_prereqs && \
    NO_PREREQ_INSTALL=True STATIC_ROOT=/staticfiles/studio paver update_assets cms --settings aws && \
    NO_PREREQ_INSTALL=True paver update_assets lms --settings aws && \
    echo "Done"
