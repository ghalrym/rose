FROM python:3.11-slim

WORKDIR /app

COPY ticketmanager /app/ticketmanager
COPY platform_theme/theme.css /app/ticketmanager/app/static/theme.css

RUN pip install --no-cache-dir -e ./ticketmanager

EXPOSE 8000

CMD ["uvicorn", "ticketmanager.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
