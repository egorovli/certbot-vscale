FROM certbot/certbot

RUN apk add --no-cache --update \
  curl \
  ca-certificates

COPY ./scripts/authenticator.py ./scripts/cleanup.py ./scripts/
