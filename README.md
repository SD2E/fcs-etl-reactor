# FCS-ETL Reactors

## Functions:

* Parameterize and launch an FCS-ETL HPC app

## Inputs:

* agave-canonical `uri` pointing to a validated manifest file
* `uri` is presented in a JSON message conforming to the `AbacoMessageAgavePath` schema

## Outputs:

* An `fcs-etl-app` job with notifications going to `notifications@sd2e.org` and the Logger service
* Automatic posts to SD2E Slack `#notifications` on success or failure
* Logs to `stderr` and the Logger service

## Requirements

* Docker 17.05+
* Installation of sd2e-cli in your `PATH` with a valid set of client credentials
* Make 3.81+
* Bash 3.2.57+
* Push access configured to DockerHub

## Test and Deploy

Broadly...

```shell
# test building the container
make container
# run pytests inside the container
make tests-local PYTESTOPTS=
# locally simulate running the reactor via message
make tests-reactor
# deploy a specially tagged container for testing
make trial-deploy
# test the deployed reactor
make tests-deployed
# deploy the production version of the reactor
make deploy
#
make postdeploy
```
