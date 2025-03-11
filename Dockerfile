FROM python:3.9-slim

WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# 캐시 문제 방지를 위해 --no-cache-dir 옵션 사용
RUN pip install --upgrade pip && \
    pip install --no-cache-dir openai==0.28.0 && \
    pip install --no-cache-dir -r requirements.txt

# 나머지 파일 복사
COPY . .

# 포트 설정
ENV PORT=5003
EXPOSE $PORT

# 환경 변수 사용
CMD gunicorn --bind 0.0.0.0:$PORT backend:app 