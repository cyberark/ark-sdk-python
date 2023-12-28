---
title: Login
description: Login Command
---

# Login

The `login` command is used to authenticate to Ark using the configured profile. When you run the command, you are prompted for the required login information (such as a password and MFA verifications).

After you have logged in, the returned access tokens are stored in a secure location on your machine. After the tokens expire, a token refresh maybe attempted (see [Refresh token](../howto/refreshing_authentication.md)) or a new login is required.

## Run
```shell linenums="0"
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