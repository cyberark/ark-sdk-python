import base64
import hashlib
import json
import os
import socket
import sys
from datetime import datetime, timedelta
from platform import uname
from typing import Dict, Final, Optional

from ark_sdk_python.common.ark_logger import get_logger
from ark_sdk_python.models import ArkProfile
from ark_sdk_python.models.auth import ArkToken, ArkTokenType

BLOCK_SIZE: Final[int] = 32
DEFAULT_BASIC_KEYRING_FOLDER: Final[str] = f'.ark_cache{os.sep}keyring'
ARK_BASIC_KEYRING_FOLDER_ENV_VAR: Final[str] = 'ARK_KEYRING_FOLDER'
ARK_BASIC_KEYRING_OVERRIDE_ENV_VAR: Final[str] = 'ARK_BASIC_KEYRING'
DBUS_SESSION_ENV_VAR: Final[str] = 'DBUS_SESSION_BUS_ADDRESS'
DEFAULT_EXPIRATION_GRACE_DELTA_SECONDS: Final[int] = 60
MAX_KEYRING_RECORD_TIME_HOURS: Final[int] = 12


class BasicKeyring:
    def __init__(self) -> None:
        self.__basic_folder_path = os.path.join(os.path.expanduser('~'), DEFAULT_BASIC_KEYRING_FOLDER)
        if ARK_BASIC_KEYRING_FOLDER_ENV_VAR in os.environ:
            self.__basic_folder_path = os.environ[ARK_BASIC_KEYRING_FOLDER_ENV_VAR]
        if not os.path.exists(self.__basic_folder_path):
            os.makedirs(self.__basic_folder_path)
        self.__keyring_file_path = os.path.join(self.__basic_folder_path, 'keyring')
        self.__mac_file_path = os.path.join(self.__basic_folder_path, 'mac')

    @staticmethod
    def __encrypt(secret: bytes, data: str) -> Dict:
        from Crypto.Cipher import AES

        # Create a cipher with the secret and default nonce
        cipher = AES.new(secret, AES.MODE_GCM)
        # Encrypt the data and generate a tag for later validation of the encryption
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        # Create the json encrypted packet (all values are also base64 encoded)
        json_k = ['nonce', 'ciphertext', 'tag']
        json_v = [base64.b64encode(x).decode('utf-8') for x in [cipher.nonce, ciphertext, tag]]
        return dict(zip(json_k, json_v))

    @staticmethod
    def __decrypt(secret: bytes, data: Dict) -> bytes:
        from Crypto.Cipher import AES

        # Prepare the base 64 decoded json
        jv = {k: base64.b64decode(data[k]) for k in data.keys()}
        # Perform the decryption and verification
        cipher = AES.new(secret, AES.MODE_GCM, nonce=jv['nonce'])
        return cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])

    def __get_current_mac(self) -> str:
        if not os.path.exists(self.__mac_file_path):
            raise Exception('Invalid Keyring')
        with open(self.__mac_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def __validate_mac_and_get_data(self) -> Optional[str]:
        mac = self.__get_current_mac()
        with open(self.__keyring_file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            data_mac = hashlib.sha256(data.encode()).hexdigest()
            if data_mac == mac:
                return data
        return None

    def __update_mac(self) -> None:
        if not os.path.exists(self.__keyring_file_path):
            raise Exception('Invalid Keyring')
        with open(self.__keyring_file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            data_mac = hashlib.sha256(data.encode()).hexdigest()
            with open(self.__mac_file_path, 'w', encoding='utf-8') as macf:
                macf.write(data_mac)

    def set_password(self, service_name: str, username: str, password: str) -> None:
        from Crypto.Util.Padding import pad

        key = pad(socket.gethostname().encode(), BLOCK_SIZE)
        existing_keyring = {}
        if os.path.exists(self.__keyring_file_path):
            data = self.__validate_mac_and_get_data()
            if not data:
                raise Exception('Keyring is invalid')
            existing_keyring = json.loads(data)
        if service_name not in existing_keyring:
            existing_keyring[service_name] = {}
        existing_keyring[service_name][username] = self.__encrypt(key, password)
        with open(self.__keyring_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_keyring, f)
        self.__update_mac()

    def get_password(self, service_name: str, username: str) -> Optional[str]:
        from Crypto.Util.Padding import pad

        key = pad(socket.gethostname().encode(), BLOCK_SIZE)
        if not os.path.exists(self.__keyring_file_path):
            return None
        data = self.__validate_mac_and_get_data()
        if not data:
            raise Exception('Keyring is invalid')
        existing_keyring = json.loads(data)
        if service_name not in existing_keyring or username not in existing_keyring[service_name]:
            return None
        return self.__decrypt(key, existing_keyring[service_name][username]).decode()

    def delete_password(self, service_name: str, username: str) -> None:
        if not os.path.exists(self.__keyring_file_path):
            return
        data = self.__validate_mac_and_get_data()
        if not data:
            raise Exception('Keyring is invalid')
        existing_keyring = json.loads(data)
        if service_name not in existing_keyring or username not in existing_keyring[service_name]:
            return
        del existing_keyring[service_name][username]
        with open(self.__keyring_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_keyring, f)
        self.__update_mac()


class ArkKeyring:
    def __init__(self, service_name: str) -> None:
        self.__service_name = service_name
        self.__logger = get_logger(self.__class__.__name__)

    @staticmethod
    def __is_docker():
        path = '/proc/self/cgroup'
        return os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path, encoding='utf-8'))

    @staticmethod
    def get_keyring(enforce_basic_keyring: bool = False):
        try:
            from keyring.backends import SecretService, macOS  # pylint: disable=unused-import
            from keyrings.cryptfile.cryptfile import CryptFileKeyring  # pylint: disable=import-error

            # Docker or WSL
            if (
                ArkKeyring.__is_docker()
                or 'Microsoft' in uname().release
                or ARK_BASIC_KEYRING_OVERRIDE_ENV_VAR in os.environ
                or enforce_basic_keyring
            ):
                return BasicKeyring()
            if sys.platform == 'win32':
                kr = CryptFileKeyring()
                kr.keyring_key = socket.gethostname()
                return kr
            elif sys.platform == 'darwin' or os.path.exists('/etc/redhat-release'):
                return BasicKeyring()
            else:
                if DBUS_SESSION_ENV_VAR not in os.environ:
                    return BasicKeyring()
                return SecretService.Keyring()
        except Exception:
            return BasicKeyring()

    def save_token(self, profile: ArkProfile, token: ArkToken, postfix: str, enforce_basic_keyring: bool = False) -> None:
        """
        Saves the specified token for a profile in the keyring.
        The keyring is the OS-based implementation or, when unavailable, a fallback to BasicKeyring is used.

        Args:
            profile (ArkProfile): _description_
            token (ArkToken): _description_
            postfix (str): _description_
            enforce_basic_keyring (bool): _description_
        """
        try:
            self.__logger.info(f'Trying to save token [{self.__service_name}-{postfix}] of profile [{profile.profile_name}]')
            kr = self.get_keyring(enforce_basic_keyring)
            kr.set_password(f'{self.__service_name}-{postfix}', profile.profile_name, token.model_dump_json())
            self.__logger.info('Saved token successfully')
        except Exception as ex:
            # Last resort fallback to basic keyring
            if not isinstance(kr, BasicKeyring) or not enforce_basic_keyring:
                self.__logger.warning(f'Falling back to basic keyring as we failed to save token with keyring [{str(kr)}]')
                return self.save_token(profile, token, postfix, True)
            self.__logger.warning(f'Failed to save token [{str(ex)}]')

    def load_token(self, profile: ArkProfile, postfix: str, enforce_basic_keyring: bool = False) -> Optional[ArkToken]:
        """
        Loads a token for a profile from the keyring.
        The keyring is the OS-based implementation or, when unavailable, a fallback to BasicKeyring is used.
        When the token has expired and no refresh token exists, the token is deleted from the keyring and nothing is returned.
        When the token has expired but a refresh token exists, the token is only deleted if the max token time has passed (48 hours).

        Args:
            profile (ArkProfile): _description_
            postfix (str): _description_
            enforce_basic_keyring (bool): _description_

        Returns:
            Optional[ArkToken]: _description_
        """
        try:
            kr = self.get_keyring(enforce_basic_keyring)
            self.__logger.info(f'Trying to load token [{self.__service_name}-{postfix}] of profile [{profile.profile_name}]')
            token_val = kr.get_password(f'{self.__service_name}-{postfix}', profile.profile_name)
            if not token_val:
                self.__logger.info('No token found')
                return None
            token = ArkToken.model_validate_json(token_val)
            if token.expires_in:
                if (
                    not token.refresh_token
                    and token.token_type != ArkTokenType.Internal
                    and (token.expires_in.replace(tzinfo=None) - timedelta(seconds=DEFAULT_EXPIRATION_GRACE_DELTA_SECONDS)) < datetime.now()
                ):
                    self.__logger.info('Token is expired and no refresh token exists')
                    kr.delete_password(f'{self.__service_name}-{postfix}', profile.profile_name)
                    return None
                elif (
                    token.refresh_token
                    and (token.expires_in.replace(tzinfo=None) + timedelta(hours=MAX_KEYRING_RECORD_TIME_HOURS)) < datetime.now()
                ):
                    self.__logger.info('Token is expired and has been in the cache for too long before another usage')
                    kr.delete_password(f'{self.__service_name}-{postfix}', profile.profile_name)
                    return None
            self.__logger.info('Loaded token successfully')
            return token
        except Exception as ex:
            # Last resort fallback to basic keyring
            if not isinstance(kr, BasicKeyring) or not enforce_basic_keyring:
                self.__logger.warning(f'Falling back to basic keyring as we failed to load token with keyring [{str(kr)}]')
                return self.load_token(profile, postfix, True)
            self.__logger.warning(f'Failed to load cached token [{str(ex)}]')
            try:
                kr.delete_password(f'{self.__service_name}-{postfix}', profile.profile_name)
            except Exception as ex_deletion:
                self.__logger.warning(f'Failed to delete failed loaded cached token [{str(ex_deletion)}]')
            return None
