import pytest
from unittest.mock import MagicMock, patch
from core.addons.modules_manager.backend.installer import ModuleInstaller


def test_is_submodule_returns_false_when_no_gitmodules(mocker):
    mocker.patch("pathlib.Path.exists", return_value=False)

    installer = ModuleInstaller()
    result = installer._is_submodule("budget")

    assert result is False


def test_is_submodule_returns_true_when_in_gitmodules(mocker):
    mock_open = mocker.mock_open(read_data='[submodule "addons/budget"]\n  path = addons/budget\n')
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open)

    installer = ModuleInstaller()
    result = installer._is_submodule("budget")

    assert result is True


def test_is_submodule_handles_uppercase(mocker):
    mock_open = mocker.mock_open(read_data='[submodule "addons/budget"]\n  path = addons/budget\n')
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open)

    installer = ModuleInstaller()
    result = installer._is_submodule("Budget")

    assert result is True