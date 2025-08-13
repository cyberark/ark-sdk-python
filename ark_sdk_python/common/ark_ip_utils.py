import ipaddress


def is_ip_address(identifier: str) -> bool:
    try:
        ipaddress.ip_address(identifier)
        return True
    except ValueError:
        return False
