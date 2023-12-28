---
title: End-user database workflow
description: End-user Database Workflow
---

# End-user database Workflow
Here is an example workflow for connecting to a database:

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
1. Get a short-lived SSO password for a database from the DPA service:
    ```shell linenums="0"
    ark exec dpa sso short-lived-password
    ```
1. One of these:
    * Log in directly to the database:
        ```shell linenums="0"
        psql "host=mytenant.postgres.cyberark.cloud user=user@cyberark.cloud.12345@postgres@mypostgres.fqdn.com"
        ```
    * Log in to the database from Ark:
        ```shell linenums="0"
        ark exec dpa databases psql --target-username postgres --target-address mypostgres.fqdn.com
        ```