ACTOR_ID=$1
MESSAGE='{"uri":"agave://data-sd2e-community/ingest/testing/1516919757000/transcriptic/rule-30_q0/1/09242017/manifest/manifest.json"}'

if [ -z "${ACTOR_ID}" ]
then
    if [ -f .ACTOR_ID ]
    then
        ACTOR_ID=$(cat .ACTOR_ID)
    fi
fi

if [ -z "${ACTOR_ID}" ]
then
    echo "Usage: $(basename $0) [ACTORID]"
    exit 1
fi

MAX_ELAPSED=600 # Maximum duration for any async task
INITIAL_PAUSE=1 # Initial delay
BACKOFF=2 # Exponential backoff

TS1=$(date "+%s")
TS2=
ELAPSED=0
PAUSE=${INITIAL_PAUSE}
JOB_STATUS=

EXEC_ID=$(abaco run -v -m "${MESSAGE}" ${ACTOR_ID} | jq -r .result.executionId)
echo "Execution ${EXEC_ID} "

while [ "${JOB_STATUS}" != "COMPLETE" ]
do
    TS2=$(date "+%s")
    ELAPSED=$((${TS2} - ${TS1}))
    JOB_STATUS=$(abaco executions -v ${ACTOR_ID} ${EXEC_ID} | jq -r .result.status)
    if [ "${ELAPSED}" -gt "${MAX_ELAPSED}" ]
    then
        break
    fi
    printf "Wait " ; printf "%0.s." $(seq 1 ${PAUSE}); printf "\n"
    sleep $PAUSE
    PAUSE=$(($PAUSE * $BACKOFF))
done
echo " ${ELAPSED} seconds"

if [ "${JOB_STATUS}" == "COMPLETE" ]
then
    abaco logs ${ACTOR_ID} ${EXEC_ID}
    exit 0
else
    echo "Error or Actor ${ACTOR_ID} couldn't process message"
    exit 1
fi
