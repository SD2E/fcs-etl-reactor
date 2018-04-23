#!/bin/bash

PLANID=$1

if [ -z "$PLANID" ]
then
    PLANID="b7cf7a75-9769-4d54-a807-ac81b92fb0af"
    echo "Defaulting to test plan $PLANID"
fi

# files-delete -S data-sd2e-community temp/flow_etl/manifest_to_fcs_etl_params/b7cf7a75-9769-4d54-a807-ac81b92fb0af

files-delete -S data-sd2e-community temp/flow_etl/manifest_to_fcs_etl_params/$PLANID
