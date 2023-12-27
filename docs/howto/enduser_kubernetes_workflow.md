---
title: Enduser Kubernetes Workflow
description: Enduser Kubernetes Workflow
---

# Enduser Kubernetes Workflow
In order to securely access to Kubernetes cluster the user will follow below steps.

First, he would install ark-sdk-python using pip if he did not do so already.

Afterwards, he would configure a profile once as follows interactivaly:
```shell
ark configure
```
Or silently:
```shell
ark configure --silent --work-with-isp --isp-username myuser
```

Now that the profile is configured, the user can login.
```shell
ark login --silent --isp-secret mysecret
```

Now that the user is logged in, the user may generate a kubectl kubeconfig file, that contain all the clusters that are accessbile to the user, based on its permissions.
```shell
ark exec dpa k8s generate-kubeconfig
```

Alternatively, by adding an optional flag and path, the config file will be generated in the provided path, overriding any existing file with the same name.
```shell
ark exec dpa k8s generate-kubeconfig -f ~/.kube
```

## Refresh SSO Certificates Workflow
Refreshing the certificate allows the user to keep using its existing generated kubeconfig file and only refresh the MFA authentication data.
The command expect a flag that indicates the output format: "-of" with one of the following arguments:

1. File - generating 2 files for certificate and private key. if chosen, a flag -f with path is mandatory
```shell
ark exec dpa sso short-lived-client-certificate -of file -f ~/home
```

2. raw - the certificate and the private key will be  printed to the client as plaintext:
```shell
ark exec dpa sso short-lived-client-certificate -of raw
```

3. base64 - the certificate and the private key will be encoded to Base64 format and will be printed to the client:
```shell
ark ark exec dpa sso short-lived-client-certificate -of base64
```
