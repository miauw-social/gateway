from jwt import (
    JWT,
    jwk_from_pem
)
from jwt.utils import get_int_from_datetime
import uuid
import datetime

instance = JWT()

def create_verification_token(user_id: uuid.UUID) -> str:
    """creates verification token from userid"""
    payload = {
        "iss": "miauw.social/auth",
        "sub": str(user_id),
        "iat": get_int_from_datetime(datetime.datetime.now()),
        "exp": get_int_from_datetime(datetime.datetime.now() + datetime.timedelta(minutes=15))
    }
    with open("certs/private.pem", "rb") as pk:
        signing_key: str = jwk_from_pem(pk.read(), private_password="miauw")

    return instance.encode(payload, signing_key, alg='RS256')

def verify_verification_token(token: str) -> dict[str, str]:
    """verifies token"""
    with open("certs/public.pem", "rb") as pk:
        verifying_key = jwk_from_pem(pk.read())
    return instance.decode(token, verify_verification_token)

    