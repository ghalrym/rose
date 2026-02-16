FROM python:3.11-slim

WORKDIR /app

COPY messagequeue /app/messagequeue

RUN pip install --no-cache-dir -e ./messagequeue

EXPOSE 8000

CMD ["uvicorn", "messagequeue.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
