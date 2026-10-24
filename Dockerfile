# Use Python 3.11 because Pillow 13 requires a supported modern Python runtime
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install the pinned application dependencies
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Install Nginx and remove cached package indexes to keep the image smaller
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/sites-enabled/default

EXPOSE 80
CMD service nginx start && gunicorn --bind 0.0.0.0:8000 app:app
