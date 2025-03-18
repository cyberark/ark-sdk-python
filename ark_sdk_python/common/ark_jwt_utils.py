from typing import Any, Dict


class ArkJWTUtils:
    @staticmethod
    def get_unverified_claims(token: str) -> Dict[str, Any]:
        from jwt import decode as jwt_decode

        return jwt_decode(
            token,
            options={'verify_signature': False},
        )
