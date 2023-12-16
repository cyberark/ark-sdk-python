---
title: Configure
description: Configure Command
---

# Configure

## Motivation
The configure command is used to create a profile to work on<br>
The profile consists of infomration regarding which authentication methods to use and what are their method settings, along with other related information such as MFA

## Running
```shell
ark configure
```

The profiles are saved to ~/.ark_profiles

No arguments are required, and interactive questions will be asked

If you wish to only supply arguments in a silent fashion, --silent can be added along with the arugments

## Usage
```shell
usage: ark configure [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                     [-dcv] [-tc TRUSTED_CERT] [-pn PROFILE_NAME] [-pd PROFILE_DESCRIPTION] [-wwis]
                     [-isam {identity,identity_service_user}] [-iu ISP_USERNAME]
                     [-iimm {pf,sms,email,otp}] [-iiu ISP_IDENTITY_URL]
                     [-iiaa ISP_IDENTITY_AUTHORIZATION_APPLICATION]

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
                        Profile name for storage
  -pd PROFILE_DESCRIPTION, --profile-description PROFILE_DESCRIPTION
                        Info about the profile
  -wwis, --work-with-isp
                        Whether to work with Identity Security Platform services
  -isam {identity,identity_service_user}, --isp-auth-method {identity,identity_service_user}
  -iu ISP_USERNAME, --isp-username ISP_USERNAME
                        Username to authenticate with
  -iimm {pf,sms,email,otp}, --isp-identity-mfa-method {pf,sms,email,otp}
                        MFA method if mfa is needed
  -iiu ISP_IDENTITY_URL, --isp-identity-url ISP_IDENTITY_URL
                        Identity url to use for authentication instead of fqdn resolving
  -iiaa ISP_IDENTITY_AUTHORIZATION_APPLICATION, --isp-identity-authorization-application ISP_IDENTITY_AUTHORIZATION_APPLICATION
                        Identity application to authorize once logged in with the service user
```