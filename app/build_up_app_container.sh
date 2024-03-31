#!/bin/bash

# .env 파일에서 환경 변수를 로드
export $(grep -v '^#' .env | xargs)

# nlpforge 이미지 ID 가져오기
image_id=$(docker images -q nlpforge)
if [ ! -z "$image_id" ]; then
    # 해당 이미지를 사용하는 모든 컨테이너를 중지하고 삭제
    containers=$(docker ps -aq -f ancestor=$image_id)
    if [ ! -z "$containers" ]; then
        echo "Stopping and removing all containers using the nlpforge image..."
        docker stop $containers
        docker rm $containers
    fi

    # 이제 이미지를 삭제
    echo "Removing existing nlpforge image..."
    docker rmi $image_id
fi

# Docker 이미지를 빌드
echo "Building nlpforge image..."
docker build --no-cache --build-arg AWS_ACCESS_KEY_ID --build-arg AWS_SECRET_ACCESS_KEY -t nlpforge .

# Docker 컨테이너를 실행
echo "Running nlpforge container..."
docker run --env-file .env -d w-p 5050:5050 nlpforge
