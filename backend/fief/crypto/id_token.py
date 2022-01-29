from datetime import datetime, timezone
from typing import Optional

from jwcrypto import jwk, jwt

from fief.models import Client
from fief.schemas.user import UserDB


def generate_id_token(
    signing_key: jwk.JWK,
    host: str,
    client: Client,
    user: UserDB,
    lifetime_seconds: int,
    *,
    encryption_key: Optional[jwk.JWK] = None,
) -> str:
    """
    Generate an ID Token for an authenticated user.

    It's a signed JWT with claims following the OpenID specification.

    :param signing_key: The JWK to sign the JWT.
    :host: The issuer host.
    :client: The client used to authenticate the user.
    :lifetime_seconds: Lifetime of the JWT.
    :encryption_key: Optional JWK to further encrypt the signed token.
    In this case, it becomes a Nested JWT, as defined in rfc7519.
    """
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + lifetime_seconds

    claims = {
        **user.get_claims(),
        "iss": host,
        "aud": [str(client.client_id)],
        "exp": exp,
        "iat": iat,
        "azp": client.client_id,
    }

    signed_token = jwt.JWT(header={"alg": "RS256"}, claims=claims)
    signed_token.make_signed_token(signing_key)

    if encryption_key is not None:
        encrypted_token = jwt.JWT(
            header={"alg": "RSA-OAEP-256", "enc": "A256CBC-HS512"},
            claims=signed_token.serialize(),
        )
        encrypted_token.make_encrypted_token(encryption_key)
        return encrypted_token.serialize()

    return signed_token.serialize()
