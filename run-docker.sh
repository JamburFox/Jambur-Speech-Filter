#!/bin/bash
IMAGE_NAME=jambur-speech-filter

# Check if the Docker image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Image $IMAGE_NAME not found. Please build it first."
    exit 1
else
    docker run -p 5000:5000 --gpus all $IMAGE_NAME
    sleep 3
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:5000
    else
        echo "Unsupported OS"
    fi
fi