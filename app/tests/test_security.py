from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core import security
from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_uses_argon2id():
    assert hash_password("secret-pass-1").startswith("$argon2id$")


def test_hash_does_not_contain_the_password():
    assert "secret-pass-1" not in hash_password("secret-pass-1")


def test_same_password_gets_a_different_hash_each_time():
    assert hash_password("secret-pass-1") != hash_password("secret-pass-1")


def test_verify_password_accepts_the_right_password():
    hashed = hash_password("secret-pass-1")
    assert verify_password("secret-pass-1", hashed) is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("secret-pass-1")
    assert verify_password("secret-pass-2", hashed) is False


def test_verify_password_returns_false_for_an_unrecognised_hash():
    assert verify_password("secret-pass-1", "this-is-not-a-hash") is False


def test_access_token_round_trip():
    token = create_access_token(42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_access_token_expires_in_about_the_configured_time():
    payload = decode_access_token(create_access_token(1))
    expires = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    remaining = expires - datetime.now(timezone.utc)
    limit = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert timedelta(0) < remaining <= limit


def test_decode_rejects_garbage():
    with pytest.raises(ValueError):
        decode_access_token("garbage")


def test_decode_rejects_an_expired_token():
    payload = {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)}
    token = jwt.encode(payload, security.SECRET_KEY, algorithm=security.ALGORITHM)
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_decode_rejects_a_tampered_token():
    token = create_access_token(1)
    header, body, signature = token.split(".")
    tampered = ".".join([header, body, signature[:-2] + ("AA" if signature[-2:] != "AA" else "BB")])
    with pytest.raises(ValueError):
        decode_access_token(tampered)
