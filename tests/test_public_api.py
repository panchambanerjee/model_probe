import model_probe
from model_probe import (
    BinaryMetrics,
    Case,
    Judge,
    LLMJudge,
    Model,
    Objective,
    OpenAIModel,
    RunResult,
    RunSummary,
    Suite,
    TIPSuite,
    TokenMatchJudge,
    Verdict,
    phryge_objectives,
    run,
    save_json,
    score_binary,
    summarize,
    summarize_by,
    summarize_by_case,
    summarize_by_two,
)
from model_probe.benchmarks.base import Objective as ObjectiveImpl
from model_probe.benchmarks.phryge import phryge_objectives as phryge_objectives_impl
from model_probe.judges.base import Judge as JudgeImpl
from model_probe.judges.base import Verdict as VerdictImpl
from model_probe.judges.heuristic import TokenMatchJudge as TokenMatchJudgeImpl
from model_probe.judges.llm import LLMJudge as LLMJudgeImpl
from model_probe.metrics import BinaryMetrics as BinaryMetricsImpl
from model_probe.metrics import score_binary as score_binary_impl
from model_probe.models.base import Model as ModelImpl
from model_probe.models.openai import OpenAIModel as OpenAIModelImpl
from model_probe.results import RunResult as RunResultImpl
from model_probe.results import RunSummary as RunSummaryImpl
from model_probe.results import save_json as save_json_impl
from model_probe.results import summarize as summarize_impl
from model_probe.results import summarize_by as summarize_by_impl
from model_probe.results import summarize_by_case as summarize_by_case_impl
from model_probe.results import summarize_by_two as summarize_by_two_impl
from model_probe.runner import run as run_impl
from model_probe.suites.base import Case as CaseImpl
from model_probe.suites.base import Suite as SuiteImpl
from model_probe.suites.tip import TIPSuite as TIPSuiteImpl


def test_version() -> None:
    assert model_probe.__version__ == "0.1.0"


def test_public_api_all() -> None:
    assert model_probe.__all__ == [
        "BinaryMetrics",
        "Case",
        "Judge",
        "LLMJudge",
        "Model",
        "Objective",
        "OpenAIModel",
        "RunResult",
        "RunSummary",
        "Suite",
        "TIPSuite",
        "TokenMatchJudge",
        "Verdict",
        "phryge_objectives",
        "run",
        "save_json",
        "score_binary",
        "summarize",
        "summarize_by",
        "summarize_by_case",
        "summarize_by_two",
    ]


def test_public_api_reexports_implementations() -> None:
    assert Case is CaseImpl
    assert Objective is ObjectiveImpl
    assert Verdict is VerdictImpl
    assert RunResult is RunResultImpl
    assert RunSummary is RunSummaryImpl
    assert BinaryMetrics is BinaryMetricsImpl
    assert Model is ModelImpl
    assert Suite is SuiteImpl
    assert Judge is JudgeImpl
    assert OpenAIModel is OpenAIModelImpl
    assert TIPSuite is TIPSuiteImpl
    assert LLMJudge is LLMJudgeImpl
    assert TokenMatchJudge is TokenMatchJudgeImpl
    assert phryge_objectives is phryge_objectives_impl
    assert run is run_impl
    assert summarize is summarize_impl
    assert summarize_by is summarize_by_impl
    assert summarize_by_two is summarize_by_two_impl
    assert summarize_by_case is summarize_by_case_impl
    assert save_json is save_json_impl
    assert score_binary is score_binary_impl
