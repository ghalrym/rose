FROM python:3.11-slim

WORKDIR /app

COPY agentmanager /app/agentmanager
COPY platform_theme/theme.css /app/agentmanager/app/static/theme.css

RUN pip install --no-cache-dir -e ./agentmanager

EXPOSE 8000

CMD ["uvicorn", "agentmanager.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
