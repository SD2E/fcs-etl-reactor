#!groovy

pipeline {
    agent any
    environment {
        REACTOR_JOB_TIMEOUT = 900
        REACTOR_JOB_GET_DIR = "job_output"
        CONTAINER_REPO    = "launch_fcs_etl_app"
        CONTAINER_TAG     = "test"
        AGAVE_CACHE_DIR   = "${HOME}/credentials_cache/${JOB_BASE_NAME}"
        AGAVE_JSON_PARSER = "jq"
        AGAVE_TENANTID    = "sd2e"
        AGAVE_APISERVER   = "https://api.sd2e.org"
        AGAVE_USERNAME    = "sd2etest"
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
        stage('Build container') {
            steps {
                sh "abaco deploy -R -B reactor-test.rc"
            }
        }
        stage('Test locally') {
            steps {
                echo "Coming Soon"
            }
        }
        stage('Deploy to Abaco') {
            steps {
                sh "abaco deploy -B reactor-test.rc ; ls -alth"
                sh "abaco list"
            }
        }
        stage('Confirm deployment') {
            steps {
                echo "Coming soon."
            }
        }
        stage('Test run') {
            steps {
                echo "Coming soon"
            }
        }
        stage('Delete reactor') {
            steps {
                echo "Coming soon"
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
