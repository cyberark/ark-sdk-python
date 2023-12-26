---
title: Exec
description: Exec Command
---

# Exec

## Motivation
The exec command is used to execute various commands based on supported services for the fitting logged in authenticators

The following services and commands are supported:

- <b>dpa</b> - Dynamic Privilege Access Services
    - <b>policies</b> - DPA Policies Management
        - <b>db</b> - DPA DB Policies
            - <b>editor</b> - DPA DB Policies Interactive Editor
        - <b>vm</b> - DPA VM Policies
            - <b>editor</b> - DPA VM Policies Interactive Editor
    - <b>certificates</b> - DPA Certificates Management
    - <b>db</b> - DPA DB Enduser Operations
    - <b>sso</b> - DPA SSO Enduser Operations
    - <b>secrets</b> - DPA Secrets Services
        - <b>db</b> - DPA DB Secrets Service
    - <b>workspaces</b> - DPA Workspaces Management
        - <b>db</b> - DPA DB Workspace Management
    - <b>k8s</b> - DPA kubernetes service

Any command has its own subcommands, with respective arguments

## Running
```shell
ark exec
```

## Usage
```shell
usage: ark exec [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                [-dcv] [-tc TRUSTED_CERT] [-pn PROFILE_NAME] [-op OUTPUT_PATH] [-rf REQUEST_FILE]
                [-rc RETRY_COUNT] [-ra]
                {dpa} ...

positional arguments:
  {dpa}

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             Whether to raw output
  -s, --silent          Silent execution, no interactiveness
  -ao, --allow-output   Allow stdout / stderr even when silent and not interactive
  -v, --verbose         Whether to verbose log
  -ls {default}, --logger-style {default}
                        Which verbose logger style to use
  -ll {DEBUG,INFO,WARN,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        Log level to use while verbose
  -dcv, --disable-cert-verification
                        Disables certificate verification on HTTPS calls, unsafe!
  -tc TRUSTED_CERT, --trusted-cert TRUSTED_CERT
                        Certificate to use for HTTPS calls
  -pn PROFILE_NAME, --profile-name PROFILE_NAME
                        Profile name to load
  -op OUTPUT_PATH, --output-path OUTPUT_PATH
                        Output file to write data to
  -rf REQUEST_FILE, --request-file REQUEST_FILE
                        Request file containing the parameters for the exec action
  -rc RETRY_COUNT, --retry-count RETRY_COUNT
                        Retry count for execution
  -ra, --refresh-auth   If possible, will try to refresh the active authentication before running the
                        actual command
```