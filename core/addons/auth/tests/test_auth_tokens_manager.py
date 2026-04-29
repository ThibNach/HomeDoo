import pytest
import time
import jwt
from core.addons.auth.backend.tokens.token_manager import TokenManager

TEST_SECRET = "a_very_long_test_secret_with_at_least_32_characters_for_safety"


def test_generate_returns_valid_token():
    manager = TokenManager(secret=TEST_SECRET)
    token = manager.generate({"person_id": 1, "name": "Test"})

    assert token is not None
    assert isinstance(token, str)


def test_verify_returns_payload_for_valid_token():
    manager = TokenManager(secret=TEST_SECRET)
    token = manager.generate({"person_id": 1, "name": "Test"})

    payload = manager.verify(token)

    assert payload is not None
    assert payload["person_id"] == 1
    assert payload["name"] == "Test"


def test_verify_returns_none_for_invalid_token():
    manager = TokenManager(secret=TEST_SECRET)

    result = manager.verify("invalid_token")

    assert result is None


def test_verify_rejects_token_signed_with_different_secret():
    manager_a = TokenManager(secret=TEST_SECRET)
    manager_b = TokenManager(secret="another_very_long_test_secret_with_at_least_32_characters_for_safety")

    token = manager_a.generate({"person_id": 1, "name": "Test"})
    result = manager_b.verify(token)

    assert result is None


def test_verify_returns_none_for_expired_token():
    manager = TokenManager(secret=TEST_SECRET, expiration_hours=0)
    token = manager.generate({"person_id": 1, "name": "Test"})

    time.sleep(1)
    result = manager.verify(token)

    assert result is None