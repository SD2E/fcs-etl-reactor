#!/bin/bash

# Sets value for an Agave app alias to make it resolvable via the Reactors.aliases library
#
# This is helpful in programmatically creating job definitions, checking statuses, etc. 
# One important thing to keep in mind: aliases are private to the user creating them. This will
# eventually change once Agave permissions support is added to AgaveDB, but presently, even
# if you and I both have an alias that claims to be named (for instance) 'org.sd2e.alias.fcs_etl_app'
# the value set and retrieved for this alias will be our own. 

AGAVE_APP_ID=$1
ALIAS="fcs_etl_app"

if [ -z "${AGAVE_APP_ID}" ]
then
    echo "Please provide an Agave app ID"
    exit 1
fi

_CHECK_EXISTS=$(apps-list ${AGAVE_APP_ID})
if [ -z "$_CHECK_EXISTS" ]
then
    echo "Can't access Agave app ${AGAVE_APP_ID}. Double check and try again."
    exit 1
fi

echo "Setting..."
docker run -t -v $HOME/.agave:/root/.agave \
           sd2e/alias_manager:0.1.0 set ${ALIAS} ${AGAVE_APP_ID}

echo "Getting new/updated value..."
docker run -t -v $HOME/.agave:/root/.agave \
           sd2e/alias_manager:0.1.0 get ${ALIAS} "None"

