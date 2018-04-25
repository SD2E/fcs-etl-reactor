#!/bin/bash

# Gets value for an given Agave App alias and validates that the app is active
#
# This is helpful in programmatically creating job definitions, checking statuses, etc. 
# One important thing to keep in mind: aliases are private to the user creating them. This will
# eventually change once Agave permissions support is added to AgaveDB, but presently, even
# if you and I both have an alias that claims to be named (for instance) 'org.sd2e.alias.fcs_etl_app'
# the value set and retrieved for this alias will be our own. 

ALIAS=$1

if [ -z "${ALIAS}" ]
then
    echo "Please provide an Reactors alias pointing to an Agave App ID"
    exit 1
fi

echo "Looking up alias..."
DOCKER_OUT=$(docker run -t -v $HOME/.agave:/root/.agave sd2e/alias_manager:0.1.0 get ${ALIAS} "None")
AGAVE_APP_ID=$(echo $DOCKER_OUT | awk '{print $3}' | tr -d '[:space:]')

echo -e "App ID: ${AGAVE_APP_ID}\nDetails:" 

apps-list --rich ${AGAVE_APP_ID}
