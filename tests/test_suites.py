from model_probe.suites.base import Case, Suite


class FakeSuite:
    name = "fake"

    def cases(self) -> list[Case]:
        return [
            Case(id="case-1", prompt="prompt one"),
            Case(
                id="case-2",
                prompt="prompt two",
                metadata={"encoding": "caesar"},
            ),
        ]


def _collect_cases(suite: Suite) -> list[Case]:
    return suite.cases()


def test_fake_suite_can_be_used_as_suite() -> None:
    suite = FakeSuite()
    cases = _collect_cases(suite)

    assert suite.name == "fake"
    assert [case.id for case in cases] == ["case-1", "case-2"]
    assert cases[0].prompt == "prompt one"
    assert cases[1].metadata == {"encoding": "caesar"}
