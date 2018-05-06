#!groovy

def JOB_ID = ''

pipeline {
    agent any
    environment {
        AGAVE_JOB_GET_DIR = "job_output"
        AGAVE_DATA_URI    = "agave://data-sd2e-community/sample/fcs-etl-application/test_data"
        AGAVE_CACHE_DIR   = "${HOME}/credentials_cache/${JOB_BASE_NAME}"
        AGAVE_JSON_PARSER = "jq"
        AGAVE_TENANTID    = "sd2e"
        AGAVE_APISERVER   = "https://api.sd2e.org"
        AGAVE_USERNAME    = credentials('sd2etest-tacc-username')
        AGAVE_PASSWORD    = credentials('sd2etest-tacc-password')
        REGISTRY_USERNAME = "sd2etest"
        REGISTRY_PASSWORD = credentials('sd2etest-dockerhub-password')
        REGISTRY_ORG      = credentials('sd2etest-dockerhub-org')
        PATH = "${HOME}/bin:${HOME}/sd2e-cloud-cli/bin:${env.PATH}"
        }
    stages {

        stage('Create Oauth client') {
            steps {
                sh "make-session-client ${JOB_BASE_NAME} ${JOB_BASE_NAME}-${BUILD_ID}"
            }
        }
        stage('Clean previous builds') {
            steps {
                echo "Removing possible leftover data and container images"
                sh "make clean || true"
            }
        }
        stage('Build app container') {
            steps {
                sh "make container"
            }
        }
        stage('Run PyTests') {
            steps {
                sh "make tests-pytest"
            }
        }
    }
    post {
        always {
            sh "delete-session-client ${JOB_BASE_NAME} ${JOB_BASE_NAME}-${BUILD_ID}"
        }
        success {
            deleteDir()
        }
    }
}
