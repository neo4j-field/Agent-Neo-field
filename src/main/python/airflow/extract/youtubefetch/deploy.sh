#!/bin/bash

PROJECT_ID=neo4j-cs-team-201901
IMAGE_NAME=agent-neo-fetch-youtube
TAG=latest

docker build -t ${IMAGE_NAME}:${TAG} .

docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

