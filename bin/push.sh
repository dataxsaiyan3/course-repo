#!/bin/sh
# This file should be run from the project's root directory
REGISTRY=$1
PROJECT=$2
VERSION=$3

set -e

# Push docker image to Azure CR repository
docker push ${REGISTRY}/${PROJECT}:${VERSION}