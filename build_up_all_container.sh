#!/bin/bash

# 환경 변수 로드 (.env 파일 내용이 자동으로 docker-compose에 적용됩니다)
source .env

# Docker Compose를 사용하여 기존 서비스를 중지하고 컨테이너 제거
echo "Stopping and removing all containers managed by docker-compose..."
docker-compose down

# Docker 이미지를 빌드 (캐시를 사용하지 않음)
echo "Building services..."
docker-compose build --no-cache

# Docker Compose를 사용하여 컨테이너 실행
echo "Running services..."
docker-compose up -d
