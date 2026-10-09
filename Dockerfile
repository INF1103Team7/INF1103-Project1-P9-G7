FROM python:3.12-slim

ENV APP_CONTAINER=1
ENV GEMINI_API_KEY=""

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
