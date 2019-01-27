void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/jasonwlcx/flask_notebook/"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "continuous-integration/jenkins"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}

pipeline {
   agent any
       stages {
          stage ('Checkout') {
             steps {
               checkout([$class: 'GitSCM', 
     	            branches: [[name: '*/develop']], 
     	            doGenerateSubmoduleConfigurations: false, 
     	            extensions: [], 
     	            submoduleCfg: [], 
     	            userRemoteConfigs: [
     	                [credentialsId: 'edf6ddc3-92f1-496c-b829-b490b2743a51', 
     	                url: 'https://github.com/jasonwlcx/flask_notebook/']]])
             }
          } // end Checkout Stage
    	  stage ('Build') {
              environment {
                def props = readProperties  interpolate: true, file: "${JENKINS_HOME}/project.properties"
                DOCKER_ENV="${props.DOCKER_ENV}"
                SECRET_KEY="${props.SECRET_KEY}"
                REACT_APP_USERS_SERVICE_URL="${props.REACT_APP_USERS_SERVICE_URL}"
                DATABASE_URL="${props.AWS_RDS_URI}"
              }
              steps {
                  sh """
                    docker-compose -f docker-compose-prod.yml rm -f && \
                    docker-compose -f docker-compose-prod.yml pull --include-deps && \
                    docker-compose -f docker-compose-prod.yml up --build -d
                  """
              }
          } // end Build Stage
          stage ('Test') {
              environment {
                def props = readProperties  interpolate: true, file: "${JENKINS_HOME}/project.properties"
                SECRET_KEY="${props.SECRET_KEY}"
                REACT_APP_USERS_SERVICE_URL="http://localhost"
              }
              steps {
                sh """
                    docker-compose -f docker-compose-prod.yml run users python manage.py test
                    docker-compose -f docker-compose-prod.yml run users flake8 project
                """
              }
          } // end of Test Stage
          stage ('Archive') {
              environment {
                DOCKER_CONFIG="${JENKINS_HOME}/.docker"
                def props = readProperties  interpolate: true, file: "${JENKINS_HOME}/project.properties"
                AWS_ACCOUNT_ID="${props.AWS_ACCOUNT_ID}"
              }
              steps {
                sh """
                    docker tag flask_notebook_client:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_client:"${BUILD_TAG}":production
                    docker tag flask_notebook_users:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users:"${BUILD_TAG}":production
                    docker tag flask_notebook_users-db:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users-db:"${BUILD_TAG}":production
                    docker tag flask_notebook_swagger:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_swagger:"${BUILD_TAG}":production
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_client:"${BUILD_TAG}":production
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users:"${BUILD_TAG}":production
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users-db:"${BUILD_TAG}":production
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_swagger:"${BUILD_TAG}":production
                """
              }
    	  } // end Archive Stage
    	  stage ( 'Cleanup') {
    	      steps {
                sh """docker-compose -f docker-compose-prod.yml down && \
                ${JENKINS_HOME}/docker_cleanup_rmi.sh
                """
              }
    	  } // end Cleanup Stage
    	  stage ( 'Deploy') {
              environment {
                def props = readProperties  interpolate: true, file: "${JENKINS_HOME}/project.properties"
                AWS_ACCOUNT_ID="${props.AWS_ACCOUNT_ID}"
                SECRET_KEY="${props.SECRET_KEY}"
                DATABASE_URL="${props.AWS_RDS_URI}"
              }
    	      steps {
                sh """ ${WORKSPACE}/docker-deploy-prod.sh """
              }
    	  } // end Cleanup Stage
       } // end Stages
       post {
            success {
                setBuildStatus("Build complete", "SUCCESS");
            }
            failure {
                setBuildStatus("Build failed", "FAILURE");
            }
        } // end Post Actions
} // end Pipeline
