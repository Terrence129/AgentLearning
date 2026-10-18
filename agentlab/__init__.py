"""AgentLab — learn agent systems by building them.

The package is intentionally small at the start. Every week of the curriculum
adds one capability to it, and the test suite in ``tests/weekNN`` is the
definition of "done" for that week.

Public surface (stable across the course):

    from agentlab import Message, ToolCall, ToolSpec, Provider, Tracer
"""

from agentlab.errors import (
    AgentError,
    BudgetExceeded,
    ConfigError,
    MaxStepsExceeded,
    ProviderError,
    SchemaValidationError,
    ToolError,
)
from agentlab.trace import TraceEvent, Tracer
from agentlab.types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    StreamEvent,
    ToolCall,
    ToolSpec,
    Usage,
)

__version__ = "0.1.0"

__all__ = [
    "AgentError",
    "BudgetExceeded",
    "CompletionRequest",
    "CompletionResponse",
    "ConfigError",
    "MaxStepsExceeded",
    "Message",
    "ProviderError",
    "SchemaValidationError",
    "StreamEvent",
    "ToolCall",
    "ToolError",
    "ToolSpec",
    "TraceEvent",
    "Tracer",
    "Usage",
    "__version__",
]
