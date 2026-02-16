FROM python:3.11-slim

WORKDIR /app

COPY discordgateway /app/discordgateway
COPY platform_theme/theme.css /app/discordgateway/app/static/theme.css

RUN pip install --no-cache-dir -e ./discordgateway

EXPOSE 8000

CMD ["uvicorn", "discordgateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
