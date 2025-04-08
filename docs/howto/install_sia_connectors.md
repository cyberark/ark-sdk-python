---
title: Install SIA connectors
description: Install SIA connectors
---

# Install SIA connectors
Here is an example workflow for installing a connector on a linux / windows box:

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
1. Create a network and connector pool:
    ```shell linenums="0"
    ark exec cmgr add-network --name mynetwork
    ark exec cmgr add-pool --name mypool --assigned-network-ids mynetwork_id
    ```
1. Install a connector:
    * Windows:
        ```shell linenums="0"
        ark exec sia access install-connector --connector-pool-id mypool_id --connector-type onprem --connector-os windows --target-machine 1.2.3.4 --username myuser --password mypassword
        ```
    * Linux:
        ```shell linenums="0"
        ark exec sia access install-connector --connector-pool-id mypool_id --connector-type aws --connector-os linux --target-machine 1.2.3.4 --username ec2-user --private-key-path /path/to/key.pem
        ```
