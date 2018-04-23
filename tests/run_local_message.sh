#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/common.sh"

MESSAGE_PATH="data/tests-deployed-message.json"
MESSAGE=
if [ -f "${DIR}/${MESSAGE_PATH}" ]; then
    MESSAGE=$(cat ${DIR}/${MESSAGE_PATH})
fi

if [ -z "${MESSAGE}" ]; then
    echo "Message not readable \@ ${MESSAGE_PATH}"
    exit 1
fi

detect_ci

source reactor.rc

TEMP=`mktemp -d $PWD/tmp.XXXXXX`
echo "Working out of $TEMP"

docker run -t -v ${HOME}/.agave:/root/.agave:rw \
           -v ${TEMP}:/mnt/ephemeral-01:rw \
           -e LOCALONLY=1 \
           -e MSG="${MESSAGE}" \
           ${DOCKER_HUB_ORG}/${DOCKER_IMAGE_TAG}:${DOCKER_IMAGE_VERSION}

if [ "$?" == 0 ]; then
    rm -rf ${TEMP}
fi
