"""Terminal-Bench OpenCode agent variant that permits local Ollama models."""

# pyright: reportMissingImports=false

from __future__ import annotations

import inspect
import json
import os
import shlex
import tempfile
from pathlib import Path

from terminal_bench.agents.installed_agents.opencode.opencode_agent import OpenCodeAgent
from terminal_bench.terminal.models import TerminalCommand
from terminal_bench.utils.template_utils import render_setup_script


class OpenCodeOllamaAgent(OpenCodeAgent):
    """OpenCode agent with Ollama env passthrough for local model smoke tests."""

    @property
    def _env(self) -> dict[str, str]:
        if self._provider != "ollama":
            return super()._env

        env: dict[str, str] = {}
        for key in ("OLLAMA_HOST", "OPENCODE_CONFIG"):
            if key in os.environ:
                env[key] = os.environ[key]
        return env

    @property
    def _install_agent_script_path(self) -> Path:
        template_path = (
            Path(inspect.getfile(OpenCodeAgent)).parent / "opencode-setup.sh.j2"
        )
        script_content = render_setup_script(
            template_path,
            self._get_template_variables(),
        )
        if self._provider == "ollama":
            script_content = f"{script_content}\n{self._opencode_config_script()}"
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".sh",
            delete=False,
        ) as temp_file:
            temp_file.write(script_content)
        os.chmod(temp_file.name, 0o755)
        return Path(temp_file.name)

    def _opencode_config_script(self) -> str:
        _, model_id = self._model_name.split("/", 1)
        base_url = os.environ.get(
            "T_BENCH_OLLAMA_BASE_URL",
            "http://172.17.0.1:11434/v1",
        )
        config = {
            "$schema": "https://opencode.ai/config.json",
            "provider": {
                "ollama": {
                    "npm": "@ai-sdk/openai-compatible",
                    "name": "Ollama",
                    "options": {
                        "baseURL": base_url,
                        "apiKey": "ollama",
                    },
                    "models": {
                        model_id: {
                            "name": model_id,
                            "limit": {
                                "context": 131072,
                                "output": 4096,
                            },
                        },
                    },
                },
            },
        }
        return "\n".join(
            [
                "mkdir -p /root/.config/opencode",
                "cat > /root/.config/opencode/opencode.json <<'OPENCODE_JSON'",
                json.dumps(config, indent=2),
                "OPENCODE_JSON",
            ],
        )

    def _run_agent_commands(self, instruction: str) -> list[TerminalCommand]:
        escaped_instruction = shlex.quote(instruction)
        return [
            TerminalCommand(
                command=(
                    f"opencode --model {self._model_name} run {escaped_instruction}; "
                    "cp -r /root/.local/share/opencode/log /logs/opencode-log || true"
                ),
                min_timeout_sec=0.0,
                max_timeout_sec=float("inf"),
                block=True,
                append_enter=True,
            ),
        ]
