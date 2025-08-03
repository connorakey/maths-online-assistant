import pytest
from unittest.mock import patch, MagicMock

import src.openai as openai_module

DUMMY_IMAGE_PATH = "dummy_image.jpg"
DUMMY_IMAGE_B64 = "fake_base64_data"
DUMMY_GUIDANCE_RESPONSE = "This is step-by-step guidance."
DUMMY_FINAL_ANSWER_RESPONSE = "42"


@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setattr(openai_module, "OPENAI_API_KEY", "fake-api-key")


@pytest.fixture
def mock_encode_base64():
    with patch(
        "src.openai.encode_image_to_base64", return_value=DUMMY_IMAGE_B64
    ) as mock:
        yield mock


@pytest.fixture
def mock_openai_response_guidance():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = DUMMY_GUIDANCE_RESPONSE
    with patch.object(
        openai_module.client.chat.completions, "create", return_value=mock_response
    ) as mock:
        yield mock


@pytest.fixture
def mock_openai_response_final():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = DUMMY_FINAL_ANSWER_RESPONSE
    with patch.object(
        openai_module.client.chat.completions, "create", return_value=mock_response
    ) as mock:
        yield mock


def test_guidance_raises_without_api_key(monkeypatch):
    monkeypatch.setattr(openai_module, "OPENAI_API_KEY", None)
    with pytest.raises(ValueError, match="OpenAI API key is not set."):
        openai_module.get_step_by_step_guidance(DUMMY_IMAGE_PATH)


def test_final_answer_raises_without_api_key(monkeypatch):
    monkeypatch.setattr(openai_module, "OPENAI_API_KEY", None)
    with pytest.raises(ValueError, match="OpenAI API key is not set."):
        openai_module.get_final_answer(DUMMY_IMAGE_PATH)


def test_get_step_by_step_guidance_success(
    mock_api_key, mock_encode_base64, mock_openai_response_guidance
):
    result = openai_module.get_step_by_step_guidance(DUMMY_IMAGE_PATH)
    assert result == DUMMY_GUIDANCE_RESPONSE
    mock_encode_base64.assert_called_once_with(DUMMY_IMAGE_PATH)
    mock_openai_response_guidance.assert_called_once()
    args, kwargs = mock_openai_response_guidance.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["max_tokens"] == 1024


def test_get_final_answer_success(
    mock_api_key, mock_encode_base64, mock_openai_response_final
):
    result = openai_module.get_final_answer(DUMMY_IMAGE_PATH)
    assert result == DUMMY_FINAL_ANSWER_RESPONSE
    mock_encode_base64.assert_called_once_with(DUMMY_IMAGE_PATH)
    mock_openai_response_final.assert_called_once()
    args, kwargs = mock_openai_response_final.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["max_tokens"] == 512
