#!/bin/bash
. .node/bin/activate && \
    paver install_node_prereqs && \
    paver update_assets cms --settings aws && \
    paver update_assets lms --settings aws && \
    echo "Done"
