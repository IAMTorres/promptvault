from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .prompt import Prompt


class PromptVault:
    """Load, manage and log prompts stored as YAML files.

    Args:
        path: Directory containing your .yaml prompt files.
        log_file: Optional path to a JSONL file where usage is logged.
    """

    def __init__(self, path: str | Path, log_file: str | Path | None = None):
        self._path = Path(path)
        if not self._path.exists():
            raise FileNotFoundError(
                f"[promptvault] Prompt directory not found: {self._path.resolve()}\n"
                "Create it and add your .yaml prompt files there."
            )
        self._log_file = Path(log_file) if log_file else None

    # ── Public API ───────────────────────────────────────────────────────────

    def load(self, name: str, version: str | None = None) -> Prompt:
        """Load a prompt by name.

        Args:
            name: Prompt name (filename without .yaml extension).
            version: Specific version string. If None, loads the latest version.

        Returns:
            A Prompt object ready to render.

        Raises:
            FileNotFoundError: if no matching prompt file is found.
        """
        candidates = self._find_files(name)
        if not candidates:
            raise FileNotFoundError(
                f"[promptvault] No prompt named '{name}' found in {self._path.resolve()}.\n"
                f"Available prompts: {self.list()}"
            )

        if version is not None:
            match = next((p for p in candidates if p["version"] == version), None)
            if match is None:
                available = [p["version"] for p in candidates]
                raise FileNotFoundError(
                    f"[promptvault] Prompt '{name}' version '{version}' not found.\n"
                    f"Available versions: {available}"
                )
            return self._parse(match)

        # Latest version = highest semver or last alphabetically
        latest = sorted(candidates, key=lambda p: p["version"])[-1]
        return self._parse(latest)

    def list(self) -> list[str]:
        """Return all prompt names available in the vault."""
        names = set()
        for f in self._path.glob("*.yaml"):
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            names.add(data.get("name", f.stem))
        return sorted(names)

    def versions(self, name: str) -> list[str]:
        """Return all available versions for a given prompt name."""
        return sorted(p["version"] for p in self._find_files(name))

    def diff(self, name: str, version_a: str, version_b: str) -> str:
        """Return a unified text diff between two versions of a prompt template."""
        import difflib

        a = self.load(name, version=version_a)
        b = self.load(name, version=version_b)
        lines_a = a.template.splitlines(keepends=True)
        lines_b = b.template.splitlines(keepends=True)
        delta = difflib.unified_diff(
            lines_a, lines_b,
            fromfile=f"{name} v{version_a}",
            tofile=f"{name} v{version_b}",
        )
        return "".join(delta) or "(no differences)"

    def log(
        self,
        name: str,
        *,
        version: str | None = None,
        rendered: str | None = None,
        response: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Append a usage record to the log file (JSONL format).

        Args:
            name: Prompt name that was used.
            version: Prompt version that was used.
            rendered: The final rendered prompt text sent to the LLM.
            response: The LLM response received.
            model: The model used (e.g. "gpt-4o", "claude-3-5-sonnet").
            extra: Any additional metadata to record.
        """
        if self._log_file is None:
            return
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": name,
            "version": version,
            "model": model,
            "rendered": rendered,
            "response": response,
            **(extra or {}),
        }
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ── Internal ─────────────────────────────────────────────────────────────

    def _find_files(self, name: str) -> list[dict]:
        results = []
        for f in self._path.glob("*.yaml"):
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if data.get("name") == name:
                results.append({**data, "_file": f})
        return results

    def _parse(self, data: dict) -> Prompt:
        return Prompt(
            name=data["name"],
            version=str(data.get("version", "1.0")),
            template=data["template"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            variables=data.get("variables", {}),
            metadata={k: v for k, v in data.items()
                      if k not in ("name", "version", "template", "description",
                                   "author", "tags", "variables", "_file")},
        )
