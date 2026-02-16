FROM python:3.11-slim

WORKDIR /app

COPY controlpanel /app/controlpanel
COPY platform_theme/theme.css /app/controlpanel/app/static/theme.css

RUN pip install --no-cache-dir -e ./controlpanel

EXPOSE 8010

CMD ["uvicorn", "controlpanel.app.main:app", "--host", "0.0.0.0", "--port", "8010"]
