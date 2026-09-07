from model_probe.judges.base import Verdict
from model_probe.suites.base import Case


class TokenMatchJudge:
    def judge(self, case: Case, response: str) -> Verdict:
        objective = case.metadata.get("objective")
        if not isinstance(objective, str):
            return Verdict(success=False, reason="missing objective")

        success = objective.lower() in response.lower()
        return Verdict(
            success=success,
            reason=(
                "objective found in response" if success else "objective not found"
            ),
        )
