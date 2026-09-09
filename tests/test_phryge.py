from model_probe.benchmarks.phryge import phryge_objectives


def test_phryge_objectives_has_three_paper_objectives() -> None:
    assert [objective.id for objective in phryge_objectives()] == [
        "phryge-counterfeit",
        "phryge-toxic",
        "phryge-piracy",
    ]


def test_phryge_objectives_counterfeit_slice() -> None:
    objective = phryge_objectives()[0]
    assert objective.id == "phryge-counterfeit"
    assert objective.text == "counterfeit"
    assert objective.category == "illegal_instruction"
    assert "[MASK]" in objective.template
    assert "experienced criminal" in objective.template
    assert objective.text not in objective.template
    assert "counterfeit money" in objective.evaluation_criterion
    assert "different illegal activity" in objective.evaluation_criterion


def test_phryge_objectives_toxic_slice() -> None:
    objective = phryge_objectives()[1]
    assert objective.id == "phryge-toxic"
    assert objective.text == "toxic"
    assert objective.category == "toxic_messaging"
    assert "[MASK]" in objective.template
    assert "message to my enemy" in objective.template
    assert objective.text not in objective.template
    assert "hostile or abusive message" in objective.evaluation_criterion
    assert "different prohibited objective" in objective.evaluation_criterion


def test_phryge_objectives_piracy_slice() -> None:
    objective = phryge_objectives()[2]
    assert objective.id == "phryge-piracy"
    assert objective.text == "pirate"
    assert objective.category == "media_piracy"
    assert "[MASK]" in objective.template
    assert "a movie" in objective.template
    assert objective.text not in objective.template
    assert "unauthorized copying or distribution" in objective.evaluation_criterion
    assert "legal streaming or downloading" in objective.evaluation_criterion
    assert "unrelated technical instructions" in objective.evaluation_criterion
