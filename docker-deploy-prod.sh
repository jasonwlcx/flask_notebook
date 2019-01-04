#!/bin/sh

    JQ="jq --raw-output --exit-status"

    register_definition() {
      if revision=$(aws ecs register-task-definition --cli-input-json "$task_def" | $JQ '.taskDefinition.taskDefinitionArn'); then
        echo "Revision: $revision"
      else
        echo "Failed to register task definition"
        return 1
      fi
    }

    update_service() {
      if [[ $(aws ecs update-service --cluster $cluster --service $service --desired-count 1 --task-definition $revision | $JQ '.service.taskDefinition') != $revision ]]; then
        echo "Error updating service."
        return 1
      fi
    }

    deploy_cluster() {

      cluster="mini-glaven-prod-cluster"
      autoScalingGroup="EC2ContainerService-mini-glaven-prod-cluster-EcsInstanceAsg-8JG3QK6IZVQ"

      if [[ $(aws ecs describe-clusters --cluster $cluster | jq -r '.clusters | .[] | .registeredContainerInstancesCount') < 1 ]]; then
        echo "Container instance not present, scaling to 1"
        aws autoscaling update-auto-scaling-group --auto-scaling-group-name $autoScalingGroup --min-size 1
      else
        echo "Register with existing container instance"
      fi


      # users
      service="mini-glaven-users-prod-service"
      template="ecs_users_prod_taskdefinition.json"
      task_template=$(cat "ecs/$template")
      task_def=$(printf "$task_template" $AWS_ACCOUNT_ID $DATABASE_URL $SECRET_KEY)
      echo "$task_def"
      register_definition
      update_service

      # client
      service="mini-glaven-client-prod-service"
      template="ecs_client_prod_taskdefinition.json"
      task_template=$(cat "ecs/$template")
      task_def=$(printf "$task_template" $AWS_ACCOUNT_ID)
      echo "$task_def"
      register_definition
      update_service

      # swagger
      service="mini-glaven-swagger-prod-service"
      template="ecs_swagger_prod_taskdefinition.json"
      task_template=$(cat "ecs/$template")
      task_def=$(printf "$task_template" $AWS_ACCOUNT_ID)
      echo "$task_def"
      register_definition
      update_service

    }

    deploy_cluster