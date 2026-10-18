"""The agent loop (week 2).

Public surface:

- ``react.run_loop``  -- the model -> tools -> observations loop itself
- ``runner.AgentRunner`` / ``runner.AgentResult`` -- run configuration and result
- ``stop.*``          -- composable termination conditions
"""

from agentlab.loop.react import LoopOutcome, StepRecord, run_loop
from agentlab.loop.runner import DEFAULT_MAX_STEPS, AgentResult, AgentRunner
from agentlab.loop.stop import (
    DEFAULT_STOP_CONDITIONS,
    AnyOf,
    FinishReasonStop,
    PredicateStop,
    RepeatedToolCallStop,
    StepState,
    StopCondition,
    StopDecision,
)

__all__ = [
    "DEFAULT_MAX_STEPS",
    "DEFAULT_STOP_CONDITIONS",
    "AgentResult",
    "AgentRunner",
    "AnyOf",
    "FinishReasonStop",
    "LoopOutcome",
    "PredicateStop",
    "RepeatedToolCallStop",
    "StepRecord",
    "StepState",
    "StopCondition",
    "StopDecision",
    "run_loop",
]
