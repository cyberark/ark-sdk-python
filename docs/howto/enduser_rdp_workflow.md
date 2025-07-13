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
1. Get a short-lived RDP token as either:
    * RDP file single usage for a windows box from the SIA service:
        ```shell linenums="0"
        ark exec sia sso short-lived-rdp-file -ta targetaddress -td targetdomain -tu targetuser
        ```
    * Password for continous usage for a windows box from the SIA service:
        ```shell linenums="0"
        ark exec sia sso short-lived-password --service DPA-RDP
        ```
1. Use the RDP file or password with mstsc or any other RDP client to connect
