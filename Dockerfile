FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint_render.sh /entrypoint_render.sh
RUN chmod +x /entrypoint_render.sh

ENTRYPOINT ["/entrypoint_render.sh"]
