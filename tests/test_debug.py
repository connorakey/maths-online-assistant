import pytest
import string
import random
import sys
from pathlib import Path
from unittest import mock

import src.debug as debug


@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    config = {"debug": {"enabled": True, "level": "debug"}}
    monkeypatch.setattr("src.debug.config", config)
    yield


def test_random_letter_string_length():
    result = debug.random_letter_string(10)
    assert isinstance(result, str)
    assert len(result) == 10


def test_random_letter_string_characters():
    result = debug.random_letter_string(20)
    assert all(c in string.ascii_letters for c in result)


def test_log_invalid_level():
    with pytest.raises(ValueError):
        debug.log("Test message", "invalid")


def test_log_disabled(monkeypatch):
    monkeypatch.setitem(debug.config["debug"], "enabled", False)
    with mock.patch("builtins.print") as mock_print:
        debug.log("Should not log", "debug")
        mock_print.assert_not_called()


def test_log_minimal_level(monkeypatch, tmp_path):
    monkeypatch.setitem(debug.config["debug"], "level", "minimal")
    monkeypatch.setattr(debug, "logs", tmp_path)
    log_file = tmp_path / debug.file_name
    debug.log("Minimal message", "minimal")
    assert log_file.exists()
    content = log_file.read_text()
    assert "Minimal message" in content


def test_log_debug_level(monkeypatch, tmp_path):
    monkeypatch.setitem(debug.config["debug"], "level", "debug")
    monkeypatch.setattr(debug, "logs", tmp_path)
    log_file = tmp_path / debug.file_name
    debug.log("Debug message", "debug")
    assert log_file.exists()
    content = log_file.read_text()
    assert "Debug message" in content


def test_clear_all_logs_deletes_log_files(monkeypatch, tmp_path):
    monkeypatch.setattr(debug, "logs", tmp_path)
    log_file = tmp_path / "test1.log"
    log_file.write_text("test")
    other_file = tmp_path / "other.txt"
    other_file.write_text("not a log")
    tmp_path.mkdir(exist_ok=True)
    result = debug.clear_all_logs()
    assert result is True
    assert not log_file.exists()
    assert other_file.exists()


def test_clear_all_logs_handles_exceptions(monkeypatch, tmp_path):
    monkeypatch.setattr(debug, "logs", tmp_path)
    log_file = tmp_path / "test2.log"
    log_file.write_text("test")
    # Simulate exception on unlink
    with mock.patch.object(Path, "unlink", side_effect=OSError("fail")):
        result = debug.clear_all_logs()
        assert result is False


def test_clear_all_logs_skips_non_log_files(monkeypatch, tmp_path):
    monkeypatch.setattr(debug, "logs", tmp_path)
    non_log_file = tmp_path / "notalog.txt"
    non_log_file.write_text("data")
    result = debug.clear_all_logs()
    assert result is True
    assert non_log_file.exists()
