FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

ENV APP_CONTAINER=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
