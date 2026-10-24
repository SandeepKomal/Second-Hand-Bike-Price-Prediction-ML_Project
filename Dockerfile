# Use Python 3.11 to support maintained Pillow releases
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Nginx
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy the custom Nginx configuration file
COPY nginx.conf /etc/nginx/sites-enabled/default

# Expose port 80 for Nginx
EXPOSE 80

# Start Nginx and Gunicorn
CMD service nginx start && gunicorn --bind 0.0.0.0:8000 app:app
