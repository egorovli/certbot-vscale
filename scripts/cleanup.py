#!/usr/bin/env python

import datetime
import json
import os
import tempfile
import urllib2

def main ():
  certbot_domain = os.getenv('CERTBOT_DOMAIN').strip()
  api_token = os.getenv('API_TOKEN').strip()

  log('processing certbot domain "{}"'.format(certbot_domain))

  tmp_data = get_tmp_data(certbot_domain)
  if not tmp_data:
    log('nothing to cleanup')
    exit(0)
  
  domain_id = tmp_data['domain_id']
  record_id = tmp_data['record_id']

  delete_record(domain_id=domain_id, record_id=record_id, token=api_token)
  log('deleted record ID "{}" from domain ID "{}"'.format(record_id, domain_id))

  delete_tmp_data(certbot_domain)
  log('deleted tmp file')

def get_tmp_data (name):
  tmp_dir = tempfile.gettempdir()
  filepath = os.path.join(tmp_dir, 'certbot_{}.json'.format(name))

  try:
    with open(filepath, 'r') as file:
      data = json.load(file)
  except IOError as err:
    if err.errno == 2:
      return None

  return data

def delete_tmp_data (name):
  tmp_dir = tempfile.gettempdir()
  filepath = os.path.join(tmp_dir, 'certbot_{}.json'.format(name))

  os.remove(filepath)

def delete_record (domain_id, record_id, token):
  request = urllib2.Request('https://api.vscale.io/v1/domains/{}/records/{}'.format(domain_id, record_id))
  request.add_header('X-Token', token)
  request.get_method = lambda: 'DELETE'

  urllib2.urlopen(request)

def log (msg, level='info'):
  ts = datetime.datetime.now().time()
  level = level.upper()
  print('[ {} ] [ {} ] cleanup: {}'.format(ts, level, msg))

if __name__ == '__main__':
  main()