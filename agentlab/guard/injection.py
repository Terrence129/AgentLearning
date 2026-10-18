"""Prompt-injection defence: treat untrusted content as data, never as orders.

The premise from ``docs/research/03-production-evals-ops.md`` §3.1: injection is
unsolved, so the goal is not "a model that cannot be fooled". The goal is a
system where **a fooled model cannot do damage**:

1. **Untrusted content is delimited and labelled** (``wrap_untrusted``) before it
   ever reaches the model, and delimiter-spoofing inside the content is escaped.
2. **Instruction hierarchy** is stated once in the system message
   (``build_guarded_messages``): system > user intent > data; data never grants
   permissions and never triggers tools.
3. **Detection is a signal, not the defence** (``scan_injection`` /
   ``screen_untrusted``): high-risk text is refused, lower-risk text is kept as
   labelled data. Regexes will miss novel attacks -- which is exactly why the
   other layers must hold when they do.
4. **Outputs are vetted** (``vet_output``): secrets, markdown-image egress and
   credential-shaped strings are redacted before leaving the agent.
5. **The lethal trifecta** (``assess_lethal_trifecta``): private data + untrusted
   content + external egress in one agent is an exfiltration waiting to happen.
   Remove one leg, or gate the egress behind human approval.

Read first: research 03 §3.1–3.2 (threat table), Simon Willison's lethal-trifecta
post, and OWASP's GenAI Top 10 2026.

Hints:
- Detect on normalized text, but return snippets from the original.
- Severities only matter for the decision: ``high`` blocks, ``medium`` flags.
- Escaping the delimiters is not cosmetic; ``</untrusted_data>`` inside content
  is how an attacker closes your data block and starts issuing orders.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from agentlab.types import Message

#: Delimiters used to frame untrusted content for the model.
UNTRUSTED_OPEN = "<untrusted_data>"
UNTRUSTED_CLOSE = "</untrusted_data>"

#: The three legs of the lethal trifecta (Willison, 2025).
TRIFECTA_LEGS: tuple[str, ...] = ("private_data", "untrusted_content", "external_egress")

#: Mitigations that break or gate one leg; unknown names are rejected.
KNOWN_MITIGATIONS: frozenset[str] = frozenset(
    {"egress_allowlist", "human_approval", "private_data_removed", "untrusted_content_removed"}
)

Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class InjectionFinding:
    """One suspicious span found in untrusted text.

    Attributes:
        category: mechanism label, e.g. ``instruction_override``, ``role_hijack``,
            ``prompt_exfiltration``, ``tool_abuse``, ``command_execution``,
            ``exfiltration``, ``hidden_content``, ``encoded_payload``.
        severity: ``high`` blocks the content, ``medium`` flags it, ``low`` is
            informational.
        start: character offset in the (normalized) scanned text.
        snippet: short excerpt around the match, safe to log.
        rule: the detector rule that fired, for tuning false positives.
    """

    category: str
    severity: Severity
    start: int
    snippet: str
    rule: str = ""


@dataclass(frozen=True, slots=True)
class TrustDecision:
    """The screen's verdict on one piece of untrusted content.

    Attributes:
        allowed: ``False`` when a high-severity finding means the content must
            not be used in this turn.
        risk: highest severity found, or ``"low"`` when nothing matched.
        findings: all findings, sorted by position.
        sanitized: the text wrapped and delimiter-escaped, ready to embed in a
            user message as labelled data (empty only if the caller discards it).
        source: provenance label, e.g. ``"tool"``, ``"web"``, ``"document"``.
    """

    allowed: bool
    risk: Severity
    findings: tuple[InjectionFinding, ...]
    sanitized: str
    source: str = "tool"


@dataclass(frozen=True, slots=True)
class VettingResult:
    """The output screen's verdict.

    Attributes:
        safe: ``True`` when nothing was found.
        reasons: sorted labels of what fired, e.g. ``secret_leak``,
            ``external_image``, ``exfiltration_url``, ``credential_like``.
        redacted: the text with offending spans replaced, safe to show a user
            or write to a trace.
    """

    safe: bool
    reasons: tuple[str, ...]
    redacted: str


@dataclass(frozen=True, slots=True)
class CapabilityProfile:
    """What one agent can touch -- the raw material for a trifecta audit."""

    reads_private_data: bool = False
    reads_untrusted_content: bool = False
    can_send_externally: bool = False


@dataclass(frozen=True, slots=True)
class TrifectaVerdict:
    """Result of a lethal-trifecta audit.

    Attributes:
        risk: ``critical`` when all three legs are present, ``elevated`` when two,
            ``low`` otherwise.
        legs_present: names from ``TRIFECTA_LEGS`` that are true.
        required_controls: controls that must exist before this agent may run
            unattended (empty below two legs).
        blocked: ``True`` when all three legs are present and no known mitigation
            was declared.
    """

    risk: Severity
    legs_present: tuple[str, ...]
    required_controls: tuple[str, ...]
    blocked: bool


def wrap_untrusted(content: str, *, source: str = "tool") -> str:
    """Frame ``content`` as labelled data for a model message.

    Contract:
        - output is ``<untrusted_data source="...">\\n<content>\\n</untrusted_data>``;
        - occurrences of either delimiter *inside* ``content`` are escaped so the
          payload cannot close the block early;
        - zero-width characters are stripped (they exist only to hide text);
        - the original content is otherwise preserved verbatim.

    Hint: escape delimiters case-insensitively; an attacker does not have to
    match your capitalisation.
    """
    raise NotImplementedError("Week 8 lab: implement wrap_untrusted")


def scan_injection(text: str) -> list[InjectionFinding]:
    """Scan untrusted text for known injection mechanisms.

    Contract:
        - returns findings sorted by start offset; ``[]`` for clean text;
        - detection runs on Unicode-normalized, case-folded text, but snippets
          are taken from the original;
        - categories cover at least: instruction override, role hijack, prompt
          exfiltration, tool abuse, command execution, exfiltration, hidden
          content (HTML comments / zero-width chars), encoded payloads;
        - benign business text (emails, numbers, normal instructions like "answer
          in one sentence") must produce no findings.

    Hint: start from a list of ``(category, severity, regex)`` rules, compile
    once at import time, and normalise with ``unicodedata.normalize("NFKC", ...)``
    plus ``casefold()``.
    """
    raise NotImplementedError("Week 8 lab: implement scan_injection")


def screen_untrusted(text: str, *, source: str = "tool") -> TrustDecision:
    """Scan, decide, and sanitize one piece of untrusted content.

    Contract:
        - ``risk`` is the maximum finding severity (``"low"`` when clean);
        - ``allowed = risk != "high"``: high-risk content is refused, not
          "prompted against";
        - ``sanitized`` is always ``wrap_untrusted(text, source=source)`` so the
          caller can still log/inspect what was rejected.
    """
    raise NotImplementedError("Week 8 lab: implement screen_untrusted")


def build_guarded_messages(
    *,
    system: str,
    user: str,
    untrusted: Sequence[str] = (),
    sources: Sequence[str] | None = None,
) -> list[Message]:
    """Compose a message list that states the instruction hierarchy once.

    Contract:
        - message 0 is a system message that contains ``system`` and the
          hierarchy rule (system > user > data; data never grants permissions);
        - message 1 is the user turn verbatim (``Message.user(user)``);
        - each untrusted item becomes one ``Message.user`` whose content is
          ``wrap_untrusted(item, source=source)``, in input order;
        - ``sources`` defaults to ``("tool",) * len(untrusted)``; a length
          mismatch raises ``ValueError``.
    """
    raise NotImplementedError("Week 8 lab: implement build_guarded_messages")


def vet_output(text: str, *, secrets: Sequence[str] = ()) -> VettingResult:
    """Vet model output before it reaches a user, a trace or a network call.

    Contract:
        - any non-empty string from ``secrets`` appearing in ``text`` yields the
          reason ``secret_leak`` and is replaced by ``[REDACTED]``;
        - markdown images with external URLs yield ``external_image`` and are
          replaced by ``[BLOCKED-URL]``;
        - URLs whose query string looks like a data channel (``?data=``,
          ``?token=``, ...) yield ``exfiltration_url`` and are blocked likewise;
        - credential-shaped strings (``sk-...``, ``AKIA...``) yield
          ``credential_like`` and are redacted;
        - ``reasons`` is sorted and de-duplicated; ``safe`` is ``not reasons``;
        - clean text is returned unchanged.
    """
    raise NotImplementedError("Week 8 lab: implement vet_output")


def assess_lethal_trifecta(
    profile: CapabilityProfile,
    *,
    mitigations: Sequence[str] = (),
) -> TrifectaVerdict:
    """Audit an agent for the lethal trifecta.

    Contract:
        - ``legs_present`` lists the true legs in ``TRIFECTA_LEGS`` order;
        - three legs => ``risk="critical"``, two => ``"elevated"``, else ``"low"``;
        - three legs with no mitigation => ``blocked=True`` and
          ``required_controls`` names at least ``human_approval`` and
          ``egress_allowlist``;
        - any known mitigation => ``blocked=False`` but the risk stays critical
          (a mitigation gates a leg; it does not remove the other two);
        - an unknown mitigation name raises ``ValueError`` (fail closed).
    """
    raise NotImplementedError("Week 8 lab: implement assess_lethal_trifecta")
