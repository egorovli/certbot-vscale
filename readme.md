# certbot-vscale-dns

## What is this?

`certbot-vscale-dns` is a [Docker](https://www.docker.com) image based on the latest [Certbot](https://certbot.eff.org) image for obtaining [Let's Encrypt](https://letsencrypt.org) certificates if you use [VScale](https://vscale.io) DNS management.

## How does it work?

This image extends the original [certbot/certbot image](https://hub.docker.com/r/certbot/certbot) with two scripts:

* `authenticator.py`
* `cleanup.py`

It makes a request to the [VScale API](https://developers.vscale.io/documentation/api/v1/) to create a TXT record for the DNS challenge. The record is cleaned up after verification.

## Example usage

Pass your API token (found in [the control panel](https://vscale.io/panel/settings/tokens/)) as an environment variable and mount your target volume to the container to store certificates.

Here, Docker's volume `srv_letsencrypt-data` is mounted, but you can use any other directory.

```sh
$ docker run \
  --rm \
  --name certbot \
  -e API_TOKEN=[...] \
  -v srv_letsencrypt-data:/etc/letsencrypt \
  egorovli/certbot-vscale certonly \
  --manual \
  --agree-tos \
  --manual-public-ip-logging-ok \
  --noninteractive \
  --email dev@example.org \
  --preferred-challenges=dns \
  --manual-auth-hook ./scripts/authenticator.py \
  --manual-cleanup-hook ./scripts/cleanup.py \
  -d 'example.org' \
  -d '*.example.org'
```