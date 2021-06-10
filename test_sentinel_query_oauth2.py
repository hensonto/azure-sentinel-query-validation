#!/usr/bin/env python3

import requests
import urllib3
import json
import os
import sys
import yaml

from pathlib import Path

class bcolors:
  OK = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

def get_token(url, resource, username, password):
  payload = {
    'grant_type': 'client_credentials',
    'client_id': username,
    'client_secret': password,
    'Content-Type': 'x-www-form-urlencoded',
    'resource': resource,
  }
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  ApiReturn = requests.post(url, data=payload, verify=False)
  ApiToken = json.loads(ApiReturn.content)['access_token']
  return { 'Authorization': str('Bearer ' + ApiToken), 'Content-Type': 'application/json' }

def ensure_environment(variable):
  if variable not in os.environ:
    raise EnvironmentError("Missing environment variable {}.".format(variable))

ensure_environment('AAD_TENANT_ID')
ensure_environment('AAD_CLIENT_ID')
ensure_environment('AAD_CLIENT_SECRET')
ensure_environment('ALA_WORKSPACE_ID')

workspace_id = os.environ['ALA_WORKSPACE_ID']
tenant_id = os.environ['AAD_TENANT_ID']
client_id = os.environ['AAD_CLIENT_ID']
client_secret = os.environ['AAD_CLIENT_SECRET']
login_url = 'https://login.microsoftonline.com/' + tenant_id + '/oauth2/token'
resource = 'https://api.loganalytics.io/'
url = 'https://api.loganalytics.io/v1/workspaces/' + workspace_id + '/query'
path = sys.argv[1]

if not os.path.isdir(path):
  raise OSError("Folder not found {}.".format(path))

headers = get_token(login_url, resource, client_id, client_secret)

ok = 0
warn = 0
fail = 0
http_fail = 0
connection_fail = 0
timeout_fail = 0
request_fail = 0

for file_path in Path(path).glob('**/*.yaml'):
  try:
    file_name = os.path.basename(file_path)
    with open(file_path) as f:
      rule = yaml.safe_load(f)
      params = {
        'query': rule['query']
      }
    result = requests.get(url, params=params, headers=headers, verify=False)
    result.raise_for_status()
    rows = len(result.json()['tables'][0]['rows'])
    if rows == 0:
      color = bcolors.WARNING
      warn = warn + 1
    else:
      color = bcolors.OK
      ok = ok + 1
    print(color + '[GOOD][' + file_name + '] result count: ' + str(rows) + bcolors.ENDC)
  except requests.exceptions.HTTPError as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] HTTP Error: ' + result.text + bcolors.ENDC)
    http_fail = http_fail + 1
  except requests.exceptions.ConnectionError as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] Connection Error: ' + str(e) + bcolors.ENDC)
    connection_fail = connection_fail + 1
  except requests.exceptions.Timeout as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] Timeout Error: ' + str(e) + bcolors.ENDC)
    timeout_fail = timeout_fail + 1
  except requests.exceptions.RequestException as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] Requests Error: ' + str(e) + bcolors.ENDC)
    request_fail = request_fail + 1
  except Exception as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] Exception: ' + str(e) + bcolors.ENDC)
    fail = fail + 1

print('')
print('GOOD: ' + str(ok))
print('WARN: ' + str(warn))
print('HTTP Error: ' + str(http_fail))
print('Connection Error: ' + str(connection_fail))
print('Timeout: ' + str(timeout_fail))
print('Request Error: ' + str(request_fail))
print('FAIL: ' + str(fail))
print('TOTAL: ' + str(ok + warn + fail + http_fail + connection_fail + timeout_fail + request_fail))
print('')
print('DONE')
