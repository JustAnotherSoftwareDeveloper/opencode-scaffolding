"""Direct-call tests for evaluation process adapters and agent configuration."""

from __future__ import annotations

import importlib
import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from lib.agent_eval_suite import core

pytestmark = pytest.mark.unit


def test_evaluation_core_preflight_cases_and_generated_task(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Report framework versions and materialize a generated task."""
    monkeypatch.setattr(
        core.importlib,
        "import_module",
        lambda name: SimpleNamespace(__version__=f"{name}-version"),
    )
    monkeypatch.setattr(core.shutil, "which", lambda _: "/usr/bin/tb")
    status = core.preflight_frameworks()
    assert status.inspect_ai == "inspect_ai-version"
    assert status.terminal_bench == "terminal_bench-version"
    assert status.tb_executable == "/usr/bin/tb"
    assert core.list_cases()[0]["case_id"] == core.CASES[0].case_id

    monkeypatch.setattr(core.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError, match="not found on PATH"):
        core.preflight_frameworks()

    monkeypatch.setattr(core.shutil, "which", lambda _: "/usr/bin/tb")
    monkeypatch.setattr(
        core.importlib, "import_module", lambda _: SimpleNamespace()
    )
    fallback_status = core.preflight_frameworks()
    assert fallback_status.inspect_ai == "installed"
    assert fallback_status.terminal_bench == "installed"

    task_path = core.write_inspect_task(tmp_path / "nested" / "task.py")
    generated = task_path.read_text(encoding="utf-8")
    assert task_path.is_file()
    assert "@task" in generated
    assert "opencode_workflow_score" in generated
    assert core.CASES[0].case_id in generated


def test_evaluation_core_builds_inspect_and_terminal_bench_commands(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Pass options, working directory, and capture settings to subprocesses."""
    calls: list[tuple[list[str], dict[str, object]]] = []

    def run(command: list[str], **kwargs: object):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="out", stderr="err")

    monkeypatch.setattr(core.subprocess, "run", run)
    task_file = tmp_path / "generated.py"
    task_file.write_text("pass\n", encoding="utf-8")
    logs = tmp_path / "logs"
    result = core.run_inspect_eval(task_file, "local/model", logs, 3)
    assert result.stdout == "out"
    assert calls[0][0] == [
        "inspect", "eval", "generated.py", "--model", "local/model",
        "--log-dir", str(logs), "--limit", "3",
    ]
    assert calls[0][1]["cwd"] == tmp_path
    assert calls[0][1]["capture_output"] is True

    core.run_inspect_eval(task_file, "local/model")
    assert calls[1][0] == [
        "inspect", "eval", "generated.py", "--model", "local/model"
    ]

    core.run_terminal_bench(
        agent="opencode",
        model="ollama/model",
        dataset="bench==1",
        output_path=tmp_path / "runs",
        agent_kwargs=("temperature=0", "region=west"),
        task_ids=("one", "two"),
        n_tasks=2,
        n_concurrent=4,
        no_rebuild=True,
        no_cleanup=True,
    )
    assert calls[2][0] == [
        "tb", "run", "--model", "ollama/model", "--dataset", "bench==1",
        "--output-path", str(tmp_path / "runs"), "--n-concurrent", "4",
        "--no-upload-results", "--agent", "opencode", "--agent-kwarg",
        "temperature=0", "--agent-kwarg", "region=west", "--task-id", "one",
        "--task-id", "two", "--n-tasks", "2", "--no-rebuild", "--no-cleanup",
    ]

    core.run_terminal_bench(
        agent="ignored",
        agent_import_path="custom.agent:Agent",
        model="provider/model",
        dataset="dataset",
        output_path=tmp_path,
    )
    assert calls[3][0][-2:] == ["--agent-import-path", "custom.agent:Agent"]


def _fake_terminal_bench_modules() -> dict[str, ModuleType]:
    """Provide the external Terminal-Bench imports needed by the adapter."""
    names = (
        "terminal_bench",
        "terminal_bench.agents",
        "terminal_bench.agents.installed_agents",
        "terminal_bench.agents.installed_agents.opencode",
        "terminal_bench.agents.installed_agents.opencode.opencode_agent",
        "terminal_bench.terminal",
        "terminal_bench.terminal.models",
        "terminal_bench.utils",
        "terminal_bench.utils.template_utils",
    )
    modules = {name: ModuleType(name) for name in names}

    class OpenCodeAgent:
        def __init__(self, provider: str, model: str) -> None:
            self._provider = provider
            self._model_name = model

        @property
        def _env(self) -> dict[str, str]:
            return {"BASE_ENV": "present"}

        def _get_template_variables(self) -> dict[str, str]:
            return {"model": self._model_name}

    @dataclass
    class TerminalCommand:
        command: str
        min_timeout_sec: float
        max_timeout_sec: float
        block: bool
        append_enter: bool

    for package in (
        "terminal_bench",
        "terminal_bench.agents",
        "terminal_bench.agents.installed_agents",
        "terminal_bench.agents.installed_agents.opencode",
        "terminal_bench.terminal",
        "terminal_bench.utils",
    ):
        modules[package].__path__ = []  # type: ignore[attr-defined]
    modules[
        "terminal_bench.agents.installed_agents.opencode.opencode_agent"
    ].OpenCodeAgent = OpenCodeAgent
    modules["terminal_bench.terminal.models"].TerminalCommand = TerminalCommand
    modules["terminal_bench.utils.template_utils"].render_setup_script = (
        lambda template_path, variables: (
            f"setup {template_path.name} {variables['model']}"
        )
    )
    return modules


def test_terminal_bench_agent_preserves_provider_environment_and_commands(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Expose Ollama settings and render model-specific agent commands."""
    for name, module in _fake_terminal_bench_modules().items():
        monkeypatch.setitem(sys.modules, name, module)
    module_name = "lib.agent_eval_suite.tb_opencode_ollama_agent"
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    agent_module = importlib.import_module(module_name)
    agent = agent_module.OpenCodeOllamaAgent("ollama", "ollama/qwen")

    monkeypatch.setenv("OLLAMA_HOST", "http://ollama.local")
    monkeypatch.setenv("OPENCODE_CONFIG", "/tmp/config.json")
    monkeypatch.setenv("OTHER_SECRET", "not-forwarded")
    assert agent._env == {
        "OLLAMA_HOST": "http://ollama.local",
        "OPENCODE_CONFIG": "/tmp/config.json",
    }
    agent._provider = "openai"
    assert agent._env == {"BASE_ENV": "present"}
    agent._provider = "ollama"

    template_dir = tmp_path / "terminal_bench" / "opencode"
    template_dir.mkdir(parents=True)
    template = template_dir / "opencode-setup.sh.j2"
    template.write_text("template", encoding="utf-8")
    monkeypatch.setattr(
        agent_module.inspect,
        "getfile",
        lambda _: str(template_dir / "agent.py"),
    )
    install_script = tmp_path / "install.sh"
    monkeypatch.setattr(
        agent_module.tempfile,
        "NamedTemporaryFile",
        lambda mode, **_: install_script.open(mode, encoding="utf-8"),
    )
    monkeypatch.setenv("T_BENCH_OLLAMA_BASE_URL", "http://custom/v1")
    path = agent._install_agent_script_path
    content = path.read_text(encoding="utf-8")
    assert path == install_script
    assert os.stat(path).st_mode & 0o777 == 0o755
    assert '"baseURL": "http://custom/v1"' in content
    assert '"qwen"' in content
    assert "OPENCODE_JSON" in content

    monkeypatch.delenv("T_BENCH_OLLAMA_BASE_URL")
    assert '"baseURL": "http://172.17.0.1:11434/v1"' in (
        agent._opencode_config_script()
    )

    commands = agent._run_agent_commands("echo 'hello world'")
    assert len(commands) == 1
    assert shlex.quote("echo 'hello world'") in commands[0].command
    assert "--model ollama/qwen" in commands[0].command
    assert commands[0].block and commands[0].append_enter
