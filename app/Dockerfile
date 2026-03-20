FROM python:3.11-slim

WORKDIR /app
ARG APP_BUILD_SHA=local
ARG APP_BUILD_TIME=local-dev

ENV APP_BUILD_SHA=$APP_BUILD_SHA
ENV APP_BUILD_TIME=$APP_BUILD_TIME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

