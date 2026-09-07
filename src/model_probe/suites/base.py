from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    metadata: dict[str, object] = field(default_factory=dict)


class Suite(Protocol):
    name: str

    def cases(self) -> list[Case]:
        ...
