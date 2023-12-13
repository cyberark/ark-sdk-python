---
title: Cache
description: Cache Command
---

# Cache

## Motivation
As the CLI is mostly managed in a cached fashion, we can use the ark cache command in order to clear / control the cache

Right now, only clearing the entire cache is supported and only for local filesystem cache type


## Running
```shell
ark cache
```


## Usage
```shell
usage: ark cache [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-dcv] [-tc TRUSTED_CERT] {clear} ...

positional arguments:
  {clear}
    clear               Clears all profiles cache

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