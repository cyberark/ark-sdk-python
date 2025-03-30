---
title: End-user rdp workflow
description: End-user rdp Workflow
---

# End-user rdp Workflow
Here is an example workflow for connecting to a windows box using rdp:

1. Install Ark SDK: `pip3 install ark-sdk-python`
1. Create a profile:  
    * Interactively:
        ```shell linenums="0"
        ark configure
        ```
    * Silently:
        ```shell linenums="0"
        ark configure --silent --work-with-isp --isp-username myuser
        ```
1. Log in to Ark:
    ```shell linenums="0"
    ark login --silent --isp-secret <my-ark-secret>
    ```
1. Get a short-lived SSO RDP file for a windows box from the SIA service:
    ```shell linenums="0"
    ark exec dpa sso short-lived-rdp-file -ta targetaddress -td targetdomain -tu targetuser
    ```
1. Use the RDP file with mstsc or any other RDP client to connect
