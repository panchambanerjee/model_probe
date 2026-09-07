import base64

from model_probe.suites.base import Case, Suite
from model_probe.suites.tip import CAESAR_SHIFT, OBJECTIVE, TIPSuite


def _collect_cases(suite: Suite) -> list[Case]:
    return suite.cases()


def _encode_caesar(text: str, shift: int) -> str:
    chars: list[str] = []
    for char in text:
        if "A" <= char <= "Z":
            chars.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
        elif "a" <= char <= "z":
            chars.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
        else:
            chars.append(char)
    return "".join(chars)


def test_tip_suite_satisfies_protocol() -> None:
    suite = TIPSuite()
    cases = _collect_cases(suite)
    assert suite.name == "tip"
    assert len(cases) == 4


def test_tip_suite_metadata() -> None:
    cases = {case.id: case for case in TIPSuite().cases()}
    expected_ids = [
        "tip-caesar-hard",
        "tip-caesar-medium",
        "tip-base64-hard",
        "tip-base64-medium",
    ]
    assert list(cases) == expected_ids

    for case_id, encoding, difficulty in (
        ("tip-caesar-hard", "caesar", "hard"),
        ("tip-caesar-medium", "caesar", "medium"),
        ("tip-base64-hard", "base64", "hard"),
        ("tip-base64-medium", "base64", "medium"),
    ):
        assert cases[case_id].metadata == {
            "attack_type": "tip",
            "encoding": encoding,
            "difficulty": difficulty,
            "objective": OBJECTIVE,
        }


def test_tip_suite_payloads_are_encoded() -> None:
    cases = {case.id: case for case in TIPSuite().cases()}
    caesar_payload = _encode_caesar(OBJECTIVE, CAESAR_SHIFT)
    base64_payload = base64.b64encode(OBJECTIVE.encode("ascii")).decode("ascii")

    assert caesar_payload in cases["tip-caesar-hard"].prompt
    assert caesar_payload in cases["tip-caesar-medium"].prompt
    assert base64_payload in cases["tip-base64-hard"].prompt
    assert base64_payload in cases["tip-base64-medium"].prompt

    assert OBJECTIVE not in cases["tip-caesar-hard"].prompt
    assert OBJECTIVE not in cases["tip-caesar-medium"].prompt
    assert OBJECTIVE not in cases["tip-base64-hard"].prompt
    assert OBJECTIVE not in cases["tip-base64-medium"].prompt
