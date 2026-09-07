from openai import OpenAI


class OpenAIModel:
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str | None = None,
    ) -> None:
        self._model = model
        kwargs: dict[str, str] = {"api_key": api_key}
        if base_url is not None:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)

    def generate(self, prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        if not completion.choices:
            return ""
        content = completion.choices[0].message.content
        return content or ""
