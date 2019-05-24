#!/usr/bin/env python

import datetime
import json
import os
import sys
import tempfile
import time
import urllib2

def main ():
  certbot_domain = os.getenv('CERTBOT_DOMAIN').strip()
  certbot_validation = os.getenv('CERTBOT_VALIDATION').strip()
  api_token = os.getenv('API_TOKEN').strip()

  log('processing certbot domain "{}"'.format(certbot_domain))

  tld = get_tld(certbot_domain)
  log('extracted TLD "{}"'.format(tld))

  decoded_itldn = decode_idn(tld)
  itldn_utf = decoded_itldn.encode('utf-8')

  if decoded_itldn != tld:
    log('decoded international TLD "{}"'.format(itldn_utf))

  tld_id = get_domain_id(domain=decoded_itldn, token=api_token)
  if not tld_id:
    log('failed to find ID of domain "{}"'.format(itldn_utf), 'ERROR')
    exit(1)
  log('extracted ID "{}" of TLD "{}"'.format(tld_id, itldn_utf))

  record_domain = get_record_domain(certbot_domain)
  log('using record domain "{}"'.format(record_domain))

  record_id = create_txt_record(domain_id=tld_id, name=record_domain, value=certbot_validation, token=api_token)
  log('created record with ID "{}"'.format(record_id))

  tmp_file = write_tmp_data(name=certbot_domain, domain_id=tld_id, record_id=record_id)
  log('written tmp file to "{}"'.format(tmp_file))
  log('sleeping 5 seconds')

  time.sleep(5)

def get_tld (domain):
  return '.'.join(domain.split('.')[-2:])

def decode_idn (domain):
  return domain.decode('idna')

def get_record_domain (domain):
  return '_acme-challenge.{}'.format(domain)

def get_domain_id (domain, token):
  request = urllib2.Request('https://api.vscale.io/v1/domains/')
  request.add_header('X-Token', token)

  try:
    contents = urllib2.urlopen(request).read()
  except urllib2.HTTPError as err:
    print('failed to get domain ID: {} {}'.format(err.code, err.msg))
    exit(1)

  data = json.loads(contents)
  for entry in data:
    if entry['name'] == domain:
      return entry['id']

  return None

def create_txt_record (domain_id, name, value, token):
  data = {
    'name': name,
    'type': 'TXT',
    'content': value,
    'ttl': 600
  }

  body = json.dumps(data, separators=(',', ':'))

  request = urllib2.Request('https://api.vscale.io/v1/domains/{}/records/'.format(domain_id), data=body)
  request.add_header('X-Token', token)
  request.add_header('Content-Type', 'application/json')

  try:
    contents = urllib2.urlopen(request).read()
  except urllib2.HTTPError as err:
    print('failed to get domain ID: {} {}'.format(err.code, err.msg))
    exit(1)

  response = json.loads(contents)
  return response['id']

def write_tmp_data (name, domain_id, record_id):
  tmp_dir = tempfile.gettempdir()
  filepath = os.path.join(tmp_dir, 'certbot_{}.json'.format(name))
  data = { 'domain_id': domain_id, 'record_id': record_id }

  with open(filepath, 'w') as file:
    json.dump(data, file, indent=2)

  return filepath

def log (msg, level='info'):
  ts = datetime.datetime.now().time()
  level = level.upper()
  print('[ {} ] [ {} ] authenticator: {}'.format(ts, level, msg))

if __name__ == '__main__':
  main()