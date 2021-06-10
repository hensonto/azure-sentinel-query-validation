# azure-sentinel-query-validation
Python script to validate Azure Sentinel/Log analytics query

## Input Yaml
Both the tools will recursively check for a yaml file in the provided folder. One yaml file should only contain 1 query.

Basic yaml file content should only contain "query:" Example:
```yaml
name: New CloudShell User
description: 'Identifies when a user creates an Azure CloudShell for the first time. Monitor this activity to ensure only expected user are using CloudShell'
query: 'AzureActivity | extend message = tostring(parse_json(Properties).message) | extend AppId = tostring(parse_json(Claims).appid) | where AppId contains "c44b4083-3bb0-49c1-b47d-974e53cbdf3c" | where OperationName =~ "Microsoft.Portal/consoles/write" | extend timestamp = TimeGenerated, AccountCustomEntity = Caller, IPCustomEntity = CallerIpAddress'
```

You can get more samples from: https://github.com/Azure/Azure-Sentinel/tree/master/Detections

## Prerequite
Don't forget to set your environment variable
```bash
export AAD_TENANT_ID='Your Tenant ID'
export AAD_CLIENT_ID='Your Client ID'
export AAD_CLIENT_SECRET='Your Client Secret'
export ALA_WORKSPACE_ID='Your log analytics workspace id'
```

## Scope and Limitation
Make sure the filename of the yaml file is "*.yaml" the code does nto support "*.yml" but feel free to modify it.
## test_sentinel_query.py
This uses the native azure sdk to query Sentinel/Log Analytics. 

### Installation
- pip install --upgrade pip
- pip install azure-loganalytics
- pip install cryptography
- pip install msrestazure
- pip install azure-cli-core
- pip install packaging

### Usage
test_sentinel_query.py [path to yaml file]

## test_sentinel_query_oauth2.py
This uses requests and urllib to connect to Azure via oauth2 authentication

### Installation
- pip install --upgrade pip
- pip install requests
- pip install urllib3

### Usage
test_sentinel_query_oauth2.py [path to yaml file]
