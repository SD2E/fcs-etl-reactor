#!/usr/bin/env bash

source reactor.rc

TEMP=`mktemp -d $PWD/tmp.XXXXXX`
echo "Working out of $TEMP"
docker run -t -v $HOME/.agave:/root/.agave \
           -v $TEMP:/mnt/ephemeral-01 \
           -e LOCALONLY=1 \
           -e MSG='{"uri":"agave://data-sd2e-community/ingest/testing/1516919757000/transcriptic/rule-30_q0/1/09242017/manifest/manifest.json"}' \
           ${DOCKER_HUB_ORG}/${DOCKER_IMAGE_TAG}:${DOCKER_IMAGE_VERSION}
