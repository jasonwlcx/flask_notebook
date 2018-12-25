void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/jasonwlcx/flask_notebook"],
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
          } // end of Checkout Stage
    	    stage ('Build') {
              environment {
                DOCKER_ENV="prod"
                SECRET_KEY="secret_key"
                REACT_APP_USERS_SERVICE_URL="http://mini-glaven-alb-1593180345.us-west-2.elb.amazonaws.com"
              }
              steps {
                  sh """
                    docker-compose -f docker-compose-prod.yml rm -f && \
                    docker-compose -f docker-compose-prod.yml pull --include-deps && \
                    docker-compose -f docker-compose-prod.yml up --build -d --build-arg
REACT_APP_USERS_SERVICE_URL=$REACT_APP_USERS_SERVICE_URL --build-arg SECRET_KEY=$SECRET_KEY
                  """
              }
          } // end of Build Stage
          stage ('Test') {
              environment {
                SECRET_KEY="secret_key"
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
              }
              steps {
                sh """
                    docker tag flask_notebook_client:latest 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_client:production
                    docker tag flask_notebook_users:latest 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users:production
                    docker tag flask_notebook_users-db:latest 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users-db:production
                    docker tag flask_notebook_swagger:latest 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_swagger:production
                    docker push 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_client:production
                    docker push 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users:production
                    docker push 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_users-db:production
                    docker push 104352192622.dkr.ecr.us-west-2.amazonaws.com/flask_notebook_swagger:production
                """
              }
    	    }
       } // end stages
       post {
            success {
                setBuildStatus("Build complete", "SUCCESS");
            }
            failure {
                setBuildStatus("Build failed", "FAILURE");
            }
        } // end post
} // end pipeline
