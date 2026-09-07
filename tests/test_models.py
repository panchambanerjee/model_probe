from model_probe.models.base import Model


class FakeModel:
    def generate(self, prompt: str) -> str:
        return f"echo:{prompt}"


def _call_generate(model: Model, prompt: str) -> str:
    return model.generate(prompt)


def test_fake_model_can_be_used_as_model() -> None:
    model = FakeModel()
    assert _call_generate(model, "hello") == "echo:hello"
