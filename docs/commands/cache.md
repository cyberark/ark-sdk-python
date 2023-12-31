---
title: Cache
description: Cache Command
---

# Cache

Use the `cache` command to manage the Ark data cached on your machine. Currently, you can only clear the filesystem cache (not data cached in the OS's keystore). 

## Running
```shell linenums="0"
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