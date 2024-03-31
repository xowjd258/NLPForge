#!/bin/bash

# .env 파일에서 환경 변수를 로드
export $(grep -v '^#' .env | xargs)

# nlpforge 컨테이너가 실행 중인지 확인 후 종료하고 삭제
if [ $(docker ps -q -f name=nlpforge) ]; then
    echo "Stopping and removing running nlpforge container..."
    docker stop nlpforge
    docker rm nlpforge
fi

# nlpforge 이미지가 있는지 확인 후 삭제
if [ $(docker images -q nlpforge) ]; then
    echo "Removing existing nlpforge image..."
    docker rmi nlpforge
fi

# Docker 이미지를 빌드
docker build --no-cache --build-arg AWS_ACCESS_KEY_ID --build-arg AWS_SECRET_ACCESS_KEY -t nlpforge .

# Docker 컨테이너를 실행
docker run --env-file .env -d -p 5050:5050 nlpforge
