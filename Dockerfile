FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 포트 설정 추가
ENV PORT=5003
EXPOSE $PORT

# 환경 변수 사용
CMD gunicorn --bind 0.0.0.0:$PORT backend:app 