#!/bin/bash

# .env 파일에서 환경 변수를 로드
export $(cat .env | xargs)

# Docker 이미지를 빌드
docker build --no-cache --build-arg AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --build-arg AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -t NLPForge .
