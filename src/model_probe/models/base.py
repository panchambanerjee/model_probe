from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...
