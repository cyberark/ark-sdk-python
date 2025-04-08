import argparse
import tempfile

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.common.ark_jwt_utils import ArkJWTUtils
from ark_sdk_python.common.connections.ssh.ark_pty_ssh_connection import ArkPTYSSHConnection
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret
from ark_sdk_python.models.auth.ark_auth_method import IdentityServiceUserArkAuthMethodSettings
from ark_sdk_python.models.common.connections.ark_connection_command import ArkConnectionCommand
from ark_sdk_python.models.common.connections.ark_connection_credentials import ArkConnectionCredentials
from ark_sdk_python.models.common.connections.ark_connection_details import ArkConnectionDetails
from ark_sdk_python.models.services.sia.sso.ark_sia_sso_get_ssh_key import ArkSIASSOGetSSHKey
from ark_sdk_python.services.sia.sso import ArkSIASSOService


def login_to_identity_security_platform(service_user: str, service_token: str, application_name: str) -> ArkISPAuth:
    """
    This will perform login to the tenant with the given service user credentials
    Caching the logged in token is disabled and will perform a full login on each call
    Will return an identity security platform authenticated class

    Args:
        service_user (str): _description_
        service_token (str): _description_
        application_name (str): _description_

    Returns:
        ArkISPAuth: _description_
    """
    print('Logging in to the tenant')
    isp_auth = ArkISPAuth(cache_authentication=False)
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username=service_user,
            auth_method=ArkAuthMethod.IdentityServiceUser,
            auth_method_settings=IdentityServiceUserArkAuthMethodSettings(identity_authorization_application=application_name),
        ),
        secret=ArkSecret(secret=service_token),
    )
    print('Logged in successfully')
    return isp_auth


def construct_ssh_proxy_address(isp_auth: ArkISPAuth) -> str:
    """
    For a given authentication, construct the SSH proxy address
    This'll grab from the ID token of the logged in user the name of the tenant (subdomain)
    And the platform domain (cyberark.cloud)
    And will concatenante everything to construct the SSH proxy address
    will return the constructed ssh proxy address

    Args:
        isp_auth (ArkISPAuth): _description_

    Returns:
        str: _description_
    """
    token = isp_auth.token.token.get_secret_value()
    return f'{ArkJWTUtils.get_subdomain_from_token(token)}.ssh.{ArkJWTUtils.get_platform_domain_from_token(token)}'


def generate_mfa_caching_ssh_key(isp_auth: ArkISPAuth, folder: str) -> str:
    """
    This function will use the logged in user
    And generate an SSH key into a given folder
    Will return the path to the SSH key

    Args:
        isp_auth (ArkISPAuth): _description_
        temp_folder (str): _description_

    Returns:
        str: _description_
    """
    print('Generating SSH MFA Caching Key')
    sso_service = ArkSIASSOService(isp_auth=isp_auth)
    path = sso_service.short_lived_ssh_key(get_ssh_key=ArkSIASSOGetSSHKey(folder=folder))
    print(f'MFA Caching SSH Key generated to [{path}]')
    return path


def connect_and_validate_connection(ssh_key_path: str, proxy_address: str, connection_string: str, command: str) -> None:
    """
    This function will perform a connection via SSH and via SIA proxy to the target
    For the given proxy address and connection string, a connection will be made with the ssh key
    Once connected, the given command will be performed, expecting a return code of 0 as success

    Args:
        ssh_key_path (str): _description_
        proxy_address (str): _description_
        connection_string (str): _description_
        command (str): _description_
    """
    print(f'Connecting to proxy [{proxy_address}] and connection string [{connection_string}]')
    ssh_connection = ArkPTYSSHConnection()
    ssh_connection.connect(
        ArkConnectionDetails(
            address=proxy_address,
            credentials=ArkConnectionCredentials(
                user=connection_string,
                private_key_filepath=ssh_key_path,
            ),
        ),
    )
    print(f'Running test command [{command}]')
    ssh_connection.run_command(
        ArkConnectionCommand(command=command, expected_rc=0),
    )
    print('Finished Successfully!')


if __name__ == '__main__':
    # Construct an argument parser for CLI parameters for the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--service-user', required=True, help='Service user to login and perform the operation with')
    parser.add_argument('--service-token', required=True, help='Service user token to use for logging in and connecting')
    parser.add_argument(
        '--service-application',
        default='__idaptive_cybr_user_oidc',
        help='Service application to login to, defaults to cyberark ISP application',
    )
    parser.add_argument(
        '--connection-string',
        required=True,
        help='SSH connection string to use for the connection, without the proxy address.'
        'A connection string may look like the following'
        '<service-user>#<tenant_subdomain>@<target_user>@<target_address>#<optional_network_name>',
    )
    parser.add_argument('--test-command', default='ls -l', help='Test command to use once connected to the target, defaults to ls -l')

    # Parse the CLI parameters
    args = parser.parse_args()

    # Construct a temporary folder to be used for the MFA Caching SSH key generation
    # At the end of the execution, the temporary folder will be deleted alongside the SSH key
    with tempfile.TemporaryDirectory() as temp_folder:
        # Perform the flow:
        # - Login to the tenant
        # - Generate an MFA Caching SSH key
        # - Construct the ssh proxy address
        # - Connect in SSH to the proxy / target with the MFA Caching SSH Key and perform the command
        isp_auth = login_to_identity_security_platform(args.service_user, args.service_token, args.service_application)
        ssh_key_path = generate_mfa_caching_ssh_key(isp_auth, temp_folder)
        proxy_address = construct_ssh_proxy_address(isp_auth)
        connect_and_validate_connection(ssh_key_path, proxy_address, args.connection_string, args.test_command)
