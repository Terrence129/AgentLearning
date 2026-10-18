"""Command-line entry points.

``agentlab doctor`` is the first command you should run after setup. It checks
the toolchain, keys and directories, and prints exactly what is missing.

``agentlab chat`` is the week 1 deliverable: a streaming terminal chat that also
prints running token/cost totals. Once ``OpenAICompatibleProvider`` works, this
command works -- it is deliberately thin plumbing over the provider seam.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from agentlab import __version__
from agentlab.budget import Budget
from agentlab.config import Settings
from agentlab.errors import AgentError, ConfigError, ProviderError
from agentlab.providers.base import assemble_stream
from agentlab.types import CompletionRequest, Message, StreamEvent

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="AgentLab: learn agent systems by building them.",
)
console = Console()

REPO_MARKERS = ("pyproject.toml", "agentlab", "labs")


@app.command()
def version() -> None:
    """Print the AgentLab version."""
    console.print(f"agentlab {__version__}")


@app.command()
def doctor(
    strict: bool = typer.Option(False, "--strict", help="Exit non-zero when any check warns."),
    live: bool = typer.Option(False, "--live", help="Also make one tiny live model call."),
) -> None:
    """Check the environment and report exactly what is missing."""
    rows: list[tuple[str, str, str]] = []

    py_ok = sys.version_info >= (3, 11)
    rows.append(
        (
            "python",
            "ok" if py_ok else "fail",
            f"{sys.version.split()[0]} (need >= 3.11)",
        )
    )

    root = Path.cwd()
    missing = [m for m in REPO_MARKERS if not (root / m).exists()]
    rows.append(
        (
            "repo root",
            "ok" if not missing else "warn",
            str(root) if not missing else f"missing markers: {', '.join(missing)} (cd to the repo root)",
        )
    )

    env_path = root / ".env"
    rows.append(
        (
            ".env file",
            "ok" if env_path.exists() else "warn",
            "found" if env_path.exists() else "not found -- copy .env.example to .env",
        )
    )

    settings = Settings.from_env(env_file=env_path)
    if settings.providers:
        for name, cfg in sorted(settings.providers.items()):
            rows.append(("provider", "ok", f"{name}: model={cfg.model} base_url={cfg.base_url}"))
    else:
        rows.append(("provider", "fail", "no provider configured -- add OPENAI_API_KEY or DEEPSEEK_API_KEY"))

    rows.append(("default", "info", settings.default_provider))

    for label, path in (("data dir", settings.data_dir), ("trace dir", settings.trace_dir)):
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            rows.append((label, "ok", str(path.resolve())))
        except OSError as exc:
            rows.append((label, "fail", f"{path}: {exc}"))

    if live and settings.providers:
        try:
            from agentlab.providers import provider_from_settings

            provider = provider_from_settings(settings)
            response = provider.complete(
                CompletionRequest(
                    messages=[Message.user("Reply with the single word: ok")],
                    model=provider.model,
                    max_tokens=5,
                )
            )
            rows.append(
                ("live call", "ok", f"{provider.name}/{provider.model}: {response.text.strip()[:40]!r}")
            )
        except Exception as exc:  # noqa: BLE001 - doctor must report, not crash
            rows.append(("live call", "fail", f"{type(exc).__name__}: {exc}"))

    table = Table(title="AgentLab environment", show_lines=False)
    table.add_column("check", style="bold")
    table.add_column("status")
    table.add_column("detail", overflow="fold")
    styles = {"ok": "green", "warn": "yellow", "fail": "red", "info": "cyan"}
    for label, status, detail in rows:
        table.add_row(label, f"[{styles.get(status, 'white')}]{status}[/]", detail)
    console.print(table)

    failures = [r for r in rows if r[1] == "fail"]
    warnings = [r for r in rows if r[1] == "warn"]
    if failures:
        console.print(f"\n[red]{len(failures)} blocking problem(s).[/] Fix them before starting a lab.")
        raise typer.Exit(1)
    if warnings:
        console.print(
            f"\n[yellow]{len(warnings)} warning(s).[/] Labs can run, but fix these for a smooth ride."
        )
        if strict:
            raise typer.Exit(1)
        return
    console.print("\n[green]Environment looks good.[/] Run `agentlab chat` or `pytest` next.")


@app.command()
def chat(
    provider: str = typer.Option(
        None, "--provider", "-p", help="Provider name (defaults to DEFAULT_PROVIDER)."
    ),
    model: str = typer.Option(None, "--model", "-m", help="Override the configured model."),
    system: str = typer.Option(
        "You are a concise, technically precise assistant. Prefer short answers.",
        "--system",
        "-s",
        help="System prompt.",
    ),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream tokens as they arrive."),
) -> None:
    """Minimal streaming chat REPL with live token/cost accounting (week 1 lab)."""
    from agentlab.providers import build_provider

    settings = Settings.from_env()
    try:
        config = settings.provider(provider)
    except ConfigError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(2) from exc
    if model:
        config = replace(config, model=model)

    try:
        backend = build_provider(config)
    except NotImplementedError as exc:
        console.print(
            Panel(
                f"[yellow]{exc}[/]\n\nThis command starts working as soon as you finish the "
                "week 1 lab in [bold]labs/week01-provider/[/]. Run `pytest tests/week01 -m week -q` to see "
                "the specification.",
                title="Week 1 lab not implemented yet",
                border_style="yellow",
            )
        )
        raise typer.Exit(3) from exc

    budget = Budget(max_usd=settings.run_budget_usd)
    messages = [Message.system(system)]
    console.print(
        Panel(
            f"[bold]{backend.name}[/] / [cyan]{backend.model}[/]\n"
            "Commands: [bold]/reset[/] [bold]/cost[/] [bold]/quit[/]",
            title="AgentLab chat",
            border_style="cyan",
        )
    )

    while True:
        try:
            user_input = Prompt.ask("[bold blue]you[/]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]bye[/]")
            return
        command = user_input.strip().lower()
        if command in {"/quit", "/exit", "/q"}:
            console.print("[dim]bye[/]")
            return
        if command == "/reset":
            messages = [Message.system(system)]
            console.print("[dim]conversation reset[/]")
            continue
        if command == "/cost":
            console.print(f"[dim]{budget.summary()}[/]")
            continue
        if not user_input.strip():
            continue

        messages.append(Message.user(user_input))
        try:
            with console.status("[dim]thinking…[/]"):
                events: list[StreamEvent] = []
                if stream:
                    console.print("[bold green]agent[/]", end=" ")
                    for event in backend.stream(
                        __import__("agentlab.types", fromlist=["CompletionRequest"]).CompletionRequest(
                            messages=messages, model=backend.model
                        )
                    ):
                        events.append(event)
                        if event.type == "text" and event.text:
                            console.print(event.text, end="", soft_wrap=True, highlight=False)
                    console.print()
                    response = assemble_stream(events)
                else:
                    response = backend.complete(
                        __import__("agentlab.types", fromlist=["CompletionRequest"]).CompletionRequest(
                            messages=messages, model=backend.model
                        )
                    )
                    console.print(Markdown(response.text))
        except NotImplementedError as exc:
            console.print(f"\n[yellow]{exc}[/]")
            continue
        except ProviderError as exc:
            console.print(f"\n[red]provider error:[/] {exc}")
            continue
        except AgentError as exc:
            console.print(f"\n[red]{type(exc).__name__}:[/] {exc}")
            continue

        messages.append(response.message)
        cost = budget.charge(backend.model, response.usage)
        budget.add_step()
        console.print(
            f"[dim]tokens in={response.usage.input_tokens} out={response.usage.output_tokens} "
            f"| ${cost:.5f} this turn | ${budget.used_usd:.5f} total[/]"
        )
        try:
            budget.assert_ok()
        except AgentError as exc:
            console.print(f"[red]stopping:[/] {exc}")
            return


def main() -> None:
    app()


if __name__ == "__main__":
    main()
