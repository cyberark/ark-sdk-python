---
title: Profiles
description: Profiles Command
---

# Profiles

Use the `profiles` command to manage multiple users and tenants. You can create, copy, modify, and delete profiles for different users and tenant, and to list all existing profiles.

## Running
```shell linenums="0"
ark profiles
```

## Usage
```shell
usage: ark profiles [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-dcv] [-tc TRUSTED_CERT]
                    {list,show,delete,clear,clone,add} ...

positional arguments:
  {list,show,delete,clear,clone,add}
    list                List all profiles
    show                Show a profile
    delete              Delete a specific profile
    clear               Clear all profiles
    clone               Clones a profile
    add                 Adds a profile to the profiles folder from a given path

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
```