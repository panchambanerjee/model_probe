from dataclasses import dataclass


@dataclass(frozen=True)
class Objective:
    id: str
    text: str
    category: str
    template: str
    evaluation_criterion: str
