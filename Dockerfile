FROM python:3.11
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 관리 파일 복사 및 설치
COPY . .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python

# 환경 변수 설정
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    AWS_DEFAULT_REGION=us-east-1 \
    AWS_DEFAULT_OUTPUT_FORMAT=json


# 테스트 실행
RUN pytest

# 애플리케이션 실행 명령어
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5050", "-k", "uvicorn.workers.UvicornWorker", "app:app"]
