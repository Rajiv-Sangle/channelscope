"""Checks that can fail (SO-DOMAIN-08; the archive's injected +1 control).

Every check runs twice: on the real input, and on a copy with a fault injected that the check must catch. A fault
that leaves the input unchanged is refused, because a control that injects nothing proves nothing (a smoke test
here did exactly that on 2026-09-29 before this rule existed). The outcome and the control are recorded together
in a `check_result` record.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

from .models import SCHEMA_VERSION

T = TypeVar("T")


@dataclass(frozen=True)
class Outcome:
    passed: bool
    observed: dict[str, Any]


@dataclass(frozen=True)
class CheckRun(Generic[T]):
    outcome: Literal["pass", "fail"]
    observed: dict[str, Any]
    fault: str
    control: Literal["detected", "missed"]
    control_observed: dict[str, Any]


class FaultDidNothing(ValueError):
    pass


def run_check(check: Callable[[T], Outcome], inputs: T, fault: Callable[[T], T], fault_description: str) -> CheckRun:
    faulted = fault(copy.deepcopy(inputs))
    if faulted == inputs:
        raise FaultDidNothing(f"the injected fault ({fault_description}) did not change the input")
    real = check(inputs)
    control = check(faulted)
    return CheckRun(outcome="pass" if real.passed else "fail", observed=real.observed, fault=fault_description,
                    control="detected" if not control.passed else "missed", control_observed=control.observed)


def check_result_record(run: CheckRun, *, check: str, mission: str, criterion: dict[str, str],
                        provenance: dict[str, Any], synthetic: bool, note: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "type": "check_result", "synthetic": synthetic,
        "provenance": provenance, "check": check, "mission": mission, "criterion": criterion,
        "outcome": run.outcome, "control": {"fault": run.fault, "outcome": run.control},
        "observed": run.observed, "note": note,
    }
