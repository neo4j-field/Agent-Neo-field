#!/bin/bash

PROJECT_ID=sales-eng-agent-neo-project
IMAGE_NAME=agent-neo-fetch-github
TAG=latest

docker build -t ${IMAGE_NAME}:${TAG} .

docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

#todo: The gitcontainers will need temp storage to write the git repositories too before they are pushed to gcr
#echo "Running the Docker container..."
#docker run --name ${CONTAINER_NAME} --rm --tmpfs /tmp:rw,size=100M gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
#echo "Docker container is running."
