import pytest
import bcrypt
from unittest.mock import MagicMock
from core.addons.auth.backend.repository import AuthRepository


def test_create_person_with_account_uses_transaction(mocker):
    mock_database = mocker.patch("core.addons.auth.backend.repository.database")
    mock_database.execute_transaction.return_value = 42

    repo = AuthRepository()
    result = repo.create_person_with_account("Thibaut", "thi@test.com", "password123")

    mock_database.execute_transaction.assert_called_once()
    assert result == 42


def test_create_person_with_account_hashes_password(mocker):
    mock_database = mocker.patch("core.addons.auth.backend.repository.database")

    captured_callback = None
    def capture(callback):
        nonlocal captured_callback
        captured_callback = callback
        return 42
    mock_database.execute_transaction.side_effect = capture

    repo = AuthRepository()
    repo.create_person_with_account("Thibaut", "thi@test.com", "password123")

    mock_cursor = MagicMock()
    mock_database.insert_item.return_value = [{"id": 1}]
    captured_callback(mock_cursor)

    second_call_args = mock_database.insert_item.call_args_list[1]
    account_data = second_call_args[0][1]

    assert account_data["password_hash"] != "password123"
    assert bcrypt.checkpw(b"password123", account_data["password_hash"].encode())


def test_login_returns_none_when_email_not_found(mocker):
    mock_database = mocker.patch("core.addons.auth.backend.repository.database")
    mock_database.fetch_join.return_value = []

    repo = AuthRepository()
    result = repo.login("notfound@test.com", "password")

    assert result is None


def test_login_returns_none_when_wrong_password(mocker):
    mock_database = mocker.patch("core.addons.auth.backend.repository.database")
    correct_hash = bcrypt.hashpw(b"correct_password", bcrypt.gensalt()).decode()
    mock_database.fetch_join.return_value = [{
        "id": 1,
        "name": "Thibaut",
        "email": "thi@test.com",
        "password_hash": correct_hash
    }]

    repo = AuthRepository()
    result = repo.login("thi@test.com", "wrong_password")

    assert result is None


def test_login_returns_token_and_person_on_success(mocker):
    mock_database = mocker.patch("core.addons.auth.backend.repository.database")
    mock_token_manager = mocker.patch("core.addons.auth.backend.repository.token_manager")

    correct_hash = bcrypt.hashpw(b"good_password", bcrypt.gensalt()).decode()
    mock_database.fetch_join.return_value = [{
        "id": 1,
        "name": "Thibaut",
        "email": "thi@test.com",
        "password_hash": correct_hash
    }]
    mock_token_manager.generate.return_value = "fake_token_12345"

    repo = AuthRepository()
    result = repo.login("thi@test.com", "good_password")

    assert result is not None
    assert result["token"] == "fake_token_12345"
    assert result["person"]["name"] == "Thibaut"
    assert result["person"]["email"] == "thi@test.com"