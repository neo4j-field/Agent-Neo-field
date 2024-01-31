#!/bin/bash

PROJECT_ID=sales-eng-agent-neo-project
IMAGE_NAME=agent-neo-fetch-youtube
TAG=latest

docker build -t ${IMAGE_NAME}:${TAG} -f tasks/youtubefetch/Dockerfile .

docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
