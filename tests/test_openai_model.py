from unittest.mock import MagicMock, patch

from model_probe.models.base import Model
from model_probe.models.openai import OpenAIModel


def _completion(content: str | None) -> MagicMock:
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    return completion


def _call_generate(model: Model, prompt: str) -> str:
    return model.generate(prompt)


@patch("model_probe.models.openai.OpenAI")
def test_generate_returns_assistant_text(mock_openai_cls: MagicMock) -> None:
    client = mock_openai_cls.return_value
    client.chat.completions.create.return_value = _completion("hello")

    text = _call_generate(
        OpenAIModel(model="gpt-4o-mini", api_key="sk-test"),
        "hi",
    )

    assert text == "hello"
    client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hi"}],
    )


@patch("model_probe.models.openai.OpenAI")
def test_generate_returns_empty_string_when_content_missing(
    mock_openai_cls: MagicMock,
) -> None:
    client = mock_openai_cls.return_value
    client.chat.completions.create.return_value = _completion(None)

    model = OpenAIModel(model="gpt-4o-mini", api_key="sk-test")
    assert model.generate("hi") == ""


@patch("model_probe.models.openai.OpenAI")
def test_generate_returns_empty_string_when_choices_empty(
    mock_openai_cls: MagicMock,
) -> None:
    client = mock_openai_cls.return_value
    completion = MagicMock()
    completion.choices = []
    client.chat.completions.create.return_value = completion

    model = OpenAIModel(model="gpt-4o-mini", api_key="sk-test")
    assert model.generate("hi") == ""


@patch("model_probe.models.openai.OpenAI")
def test_constructor_passes_base_url(mock_openai_cls: MagicMock) -> None:
    OpenAIModel(
        model="gpt-4o-mini",
        api_key="sk-test",
        base_url="http://localhost:8000/v1",
    )
    mock_openai_cls.assert_called_once_with(
        api_key="sk-test",
        base_url="http://localhost:8000/v1",
    )


@patch("model_probe.models.openai.OpenAI")
def test_constructor_omits_base_url_when_none(mock_openai_cls: MagicMock) -> None:
    OpenAIModel(model="gpt-4o-mini", api_key="sk-test")
    mock_openai_cls.assert_called_once_with(api_key="sk-test")
