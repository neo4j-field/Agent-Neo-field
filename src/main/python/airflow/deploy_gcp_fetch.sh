#!/bin/bash

PROJECT_ID=sales-eng-agent-neo-project
IMAGE_NAME=agent-neo-fetch-gcp
TAG=latest


# Build the Docker image using the Dockerfile inside 'tasks/gcpfetch'
# Make sure to specify the correct path to the Dockerfile
docker build -t ${IMAGE_NAME}:${TAG} -f tasks/gcpfetch/Dockerfile .

# Tag the image
docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}


# docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

