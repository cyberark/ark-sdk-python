---
title: Exec
description: Exec Command
---

# Exec

You use the `exec` command is used to run commands on available services (the available services depend on the authorized user's account).

## DPA services

The following DPA commands are supported:

- `ark exec dpa`: Root command for the DBA service
    - `policies` - Policy management
        - `db` - DB policies
            - `editor` - DB policies interactive editor
        - `vm` - DPA VM policies
            - `editor` - DPA VM policies interactive editor
    - `certificates` - Certificate management
    - `databases` - Databases end-user operations
    - `sso` - SSO end-user operations
    - `secrets` - Secrets service
        - `db` - DB secrets service
    - `workspaces` - Workspaces management
        - `db` - DB workspace management
    - `k8s` - Kubernetes service

All commands have their own subcommands and respective arguments.

## Running
```shell linenums="0"
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