FROM python:3.11-slim

WORKDIR /app

COPY heartbeat /app/heartbeat

RUN pip install --no-cache-dir -e ./heartbeat

CMD ["python", "-m", "heartbeat.app.main"]
