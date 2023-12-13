import random
import string
from ipaddress import IPv4Address


class ArkRandomUtils:
    @staticmethod
    def random_ip_address():
        random.seed(random.randint(1, 10001))
        return str(IPv4Address(random.getrandbits(32)))

    @staticmethod
    def random_string(n=8):
        return ''.join(random.choices(string.ascii_letters, k=n))

    @staticmethod
    def random_password(n=10):
        return ''.join(
            random.choices(string.digits, k=1)
            + random.choices(string.ascii_lowercase, k=1)
            + random.choices(string.ascii_uppercase, k=1)
            + random.choices(string.ascii_letters + string.digits, k=n - 3)
        )
