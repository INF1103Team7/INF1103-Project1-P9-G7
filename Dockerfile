FROM python:3.12-slim

ENV APP_CONTAINER=1

WORKDIR /app

RUN pip install --no-cache-dir google-genai python-dotenv

COPY . .

CMD ["python", "main.py"]
