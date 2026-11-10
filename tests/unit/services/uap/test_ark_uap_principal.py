import pytest
from pydantic import ValidationError

from ark_sdk_python.models.services.uap.common import ArkUAPPrincipal, ArkUAPPrincipalType


def _role(name: str) -> ArkUAPPrincipal:
    return ArkUAPPrincipal(id='3e3569b1_c173_433a_8738_1a74c0d193f5', name=name, type=ArkUAPPrincipalType.ROLE)


@pytest.mark.parametrize('name', ['Administration Role', 'System Administrator', 'Three Word Role'])
def test_accepts_a_role_name_with_a_space(name):
    assert _role(name).name == name


@pytest.mark.parametrize('name', ['ADBTestsZspAccessRole', 'tina@cyberark.cloud.52355', 'a.b.c', 'role-with-dash', 'x+y'])
def test_accepts_names_without_a_space(name):
    assert _role(name).name == name


@pytest.mark.parametrize('name', [' Leading', 'Trailing ', 'Role  Two'])
def test_accepts_surrounding_and_repeated_whitespace(name):
    assert _role(name).name == name


def test_rejects_empty_name():
    with pytest.raises(ValidationError):
        _role('')
