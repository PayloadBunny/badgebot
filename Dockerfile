# Define build arguments
ARG PYTHON_VERSION=3.12.8

# Base image with Python
FROM python:${PYTHON_VERSION}-slim as python-base

# Set environment variables
ENV APP_PATH="/opt/certbot"

# Set working directory inside the container
WORKDIR $APP_PATH

# Install system dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  curl \
  nano \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . $APP_PATH

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the CMD to run the application
CMD ["python", "bot.py"]