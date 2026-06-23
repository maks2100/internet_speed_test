import json
from unittest.mock import Mock, patch

import pytest
import requests

from speed_test import download_file, load_config


def test_load_config(tmp_path, monkeypatch):
    """
    Проверяет успешную загрузку конфигурации.
    """
    config_data = {
        "url": "https://example.com/file.bin",
        "requests_count": 10,
        "timeout": 60,
    }

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(config_data),
        encoding="utf-8"
    )

    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config == config_data


def test_load_config_file_not_found(tmp_path, monkeypatch):
    """
    Проверяет выброс исключения, если конфиг отсутствует.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        load_config()


@patch("speed_test.requests.get")
def test_download_file_success(mock_get):
    """
    Проверяет успешное скачивание файла.
    """
    mock_response = Mock()
    mock_response.content = b"1234567890"
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    elapsed_time, downloaded_bytes = download_file(
        url="https://example.com/file.bin",
        timeout=10,
    )

    assert elapsed_time > 0
    assert downloaded_bytes == 10

    mock_get.assert_called_once_with(
        "https://example.com/file.bin",
        timeout=10,
    )


@patch("speed_test.requests.get")
def test_download_file_http_error(mock_get):
    """
    Проверяет обработку HTTP-ошибки.
    """
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("404 Not Found")
    )

    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        download_file(
            url="https://example.com/file.bin",
            timeout=10,
        )
