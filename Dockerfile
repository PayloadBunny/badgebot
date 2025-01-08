ARG APP_NAME=certbot
ARG PYTHON_VERSION=3.12.8

FROM python:${PYTHON_VERSION}-slim as python-base

ENV APP_PATH="/opt/certbot"

FROM python-base as builder-base

# Install dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  curl \
  git \
  build-essential
RUN rm -rf /var/lib/apt/lists/*
WORKDIR $APP_PATH

ENV cacheBUSTER 2


# Clone repository
ARG REPO_URL=https://github.com/janssensjelle/badgebot.git
ARG BRANCH=main
RUN git clone --branch $BRANCH $REPO_URL /opt/certbot

WORKDIR $APP_PATH

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the CMD to run the application, which will use environment variables passed at runtime
CMD ["python", "/opt/certbot/bot.py"]