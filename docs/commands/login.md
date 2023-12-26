---
title: Login
description: Login Command
---

# Login

The login command is used to login to the authentication methods configured for the profile

You will be asked to write a password for each respective authentication method that supports password, and alongside that, any needed MFA prompt

Once the login is done, the access tokens are stored on the computer keystore for their lifetime

Once they are expired, a consecutive login will be required

## Run
```shell
ark login
```

## Usage
```shell
usage: ark login [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                 [-dcv] [-tc TRUSTED_CERT] [-pn PROFILE_NAME] [-f] [-nss] [-st] [-ra]
                 [-isu ISP_USERNAME] [-iss ISP_SECRET]

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
  -f, --force           Whether to force login even thou token has not expired yet
  -nss, --no-shared-secrets
                        Do not share secrets between different authenticators with the
                        same username
  -st, --show-tokens    Print out tokens as well if not silent
  -ra, --refresh-auth   If a cache exists, will also try to refresh it
  -isu ISP_USERNAME, --isp-username ISP_USERNAME
                        Username to authenticate with to Identity Security Platform
  -iss ISP_SECRET, --isp-secret ISP_SECRET
                        Secret to authenticate with to Identity Security Platform
```