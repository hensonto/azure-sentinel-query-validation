#!/usr/bin/env python3

import os
import sys
import yaml

from azure.loganalytics import LogAnalyticsDataClient
from azure.common.credentials import get_azure_cli_credentials
from azure.loganalytics.models import QueryBody
from pathlib import Path

class bcolors:
  OK = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

def ensure_environment(variable):
  if variable not in os.environ:
    raise EnvironmentError("Missing environment variable {}.".format(variable))

ensure_environment('ALA_WORKSPACE_ID')

workspace_id = os.environ['ALA_WORKSPACE_ID']
path = sys.argv[1]

ok = 0
warn = 0
fail = 0

if not os.path.isdir(path):
  raise OSError("Folder not found {}.".format(path))

creds, _ = get_azure_cli_credentials(resource="https://api.loganalytics.io")
log_client = LogAnalyticsDataClient(creds)

for file_path in Path(path).glob('**/*.yaml'):
  try:
    file_name = os.path.basename(file_path)
    with open(file_path) as f:
      rule = yaml.safe_load(f)
      query = rule['query']
    result = log_client.query(workspace_id, QueryBody(**{'query': query}))
    if len(result.tables[0].rows) == 0:
      color = bcolors.WARNING
      warn = warn + 1
    else:
      color = bcolors.OK
      ok = ok + 1
    print(color + '[GOOD][' + file_name + '] result count: ' + str(len(result.tables[0].rows)) + bcolors.ENDC)
  except Exception as e:
    print(bcolors.FAIL + '[FAIL][' + file_name + '] ' + str(e) + bcolors.ENDC)
    fail = fail + 1

print('')
print('GOOD: ' + str(ok))
print('WARN: ' + str(warn))
print('FAIL: ' + str(fail))
print('TOTAL: ' + str(ok + warn + fail))
print('')
print('DONE')