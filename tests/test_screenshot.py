import os
import sys
from pathlib import Path
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
import screenshot


@pytest.fixture
def temp_dirs(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    screenshots = workspace / "screenshots"
    questions_dir = screenshots / "questions"
    answers_dir = screenshots / "answers"
    questions_dir.mkdir(parents=True, exist_ok=True)
    answers_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(screenshot, "workspace", workspace)
    monkeypatch.setattr(screenshot, "screenshots", screenshots)
    monkeypatch.setattr(screenshot, "questions_dir", questions_dir)
    monkeypatch.setattr(screenshot, "answers_dir", answers_dir)
    yield questions_dir, answers_dir


def test_random_letter_string_length_and_charset():
    s = screenshot.random_letter_string(12)
    assert len(s) == 12
    assert all(c.isalpha() for c in s)


def test_check_if_exists_true_false(temp_dirs):
    questions_dir, _ = temp_dirs
    test_file = questions_dir / "test.png"
    test_file.write_text("dummy")
    assert screenshot.check_if_exists(questions_dir, "test.png")
    assert not screenshot.check_if_exists(questions_dir, "notfound.png")


def test_capture_screenshot_creates_file(monkeypatch, temp_dirs):
    _, answers_dir = temp_dirs

    class DummyScreenshot:
        def save(self, path):
            Path(path).write_text("dummy image")

    monkeypatch.setattr(
        screenshot,
        "pyautogui",
        type(
            "DummyPyAutoGUI", (), {"screenshot": lambda region=None: DummyScreenshot()}
        ),
    )
    # Patch config
    monkeypatch.setattr(
        screenshot,
        "config",
        {"ui": {"question_region": [[0, 0], [10, 0], [10, 10], [0, 10]]}},
    )
    filename = screenshot.capture_screenshot()
    assert filename.endswith(".png")
    file_path = answers_dir / filename
    assert file_path.exists()
    assert file_path.read_text() == "dummy image"


def test_clear_all_screenshots_removes_png(monkeypatch, temp_dirs):
    questions_dir, answers_dir = temp_dirs
    # Create dummy png files
    q_file = questions_dir / "q.png"
    a_file = answers_dir / "a.png"
    q_file.write_text("dummy")
    a_file.write_text("dummy")
    # Create a non-png file
    other_file = answers_dir / "other.txt"
    other_file.write_text("dummy")
    screenshot.clear_all_screenshots()
    assert not q_file.exists()
    assert not a_file.exists()
    assert other_file.exists()


def test_clear_all_screenshots_handles_missing_dir(monkeypatch, tmp_path):
    # Patch questions_dir to a non-existent path
    monkeypatch.setattr(screenshot, "questions_dir", tmp_path / "not_exist")
    monkeypatch.setattr(screenshot, "answers_dir", tmp_path / "not_exist")
    # Should not
