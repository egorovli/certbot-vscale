FROM certbot/certbot

RUN apk add \
  --no-cache \
  --update \
  ca-certificates

COPY ./scripts/authenticator.py ./scripts/cleanup.py ./scripts/
