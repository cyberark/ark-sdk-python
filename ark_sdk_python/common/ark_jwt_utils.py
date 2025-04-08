from typing import Any, Dict


class ArkJWTUtils:
    @staticmethod
    def get_unverified_claims(token: str) -> Dict[str, Any]:
        from jwt import decode as jwt_decode

        return jwt_decode(
            token,
            options={'verify_signature': False},
        )

    @staticmethod
    def get_subdomain_from_token(token: str) -> str:
        claims = ArkJWTUtils.get_unverified_claims(token)
        return claims.get('subdomain', '')

    @staticmethod
    def get_platform_domain_from_token(token: str) -> str:
        claims = ArkJWTUtils.get_unverified_claims(token)
        return claims.get('platform_domain', '')
