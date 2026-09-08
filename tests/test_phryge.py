from model_probe.benchmarks.phryge import phryge_objectives


def test_phryge_objectives_counterfeit_slice() -> None:
    objectives = phryge_objectives()
    assert len(objectives) == 1

    objective = objectives[0]
    assert objective.id == "phryge-counterfeit"
    assert objective.category == "illegal_instruction"
    assert "[MASK]" in objective.template
    assert "experienced criminal" in objective.template
    assert objective.text not in objective.template
    assert "counterfeit money" in objective.evaluation_criterion
    assert "different illegal activity" in objective.evaluation_criterion
