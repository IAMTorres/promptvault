from __future__ import annotations
from dataclasses import dataclass, field
from string import Template
from typing import Any


@dataclass
class Prompt:
    """Represents a single loaded prompt with its metadata."""

    name: str
    version: str
    template: str
    description: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    variables: dict[str, dict] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: Any) -> str:
        """Render the prompt template with the given variables.

        Raises:
            KeyError: if a required variable is missing.
            TypeError: if a variable has the wrong type.
        """
        self._validate(kwargs)
        merged = self._apply_defaults(kwargs)
        try:
            return Template(self.template).substitute(merged)
        except KeyError as e:
            raise KeyError(
                f"[promptvault] Missing variable {e} in prompt '{self.name}' v{self.version}. "
                f"Expected variables: {list(self.variables.keys())}"
            ) from e

    def _validate(self, kwargs: dict) -> None:
        for var_name, var_meta in self.variables.items():
            required = var_meta.get("required", True)
            has_default = "default" in var_meta
            if required and not has_default and var_name not in kwargs:
                raise KeyError(
                    f"[promptvault] Required variable '{var_name}' missing for prompt "
                    f"'{self.name}' v{self.version}."
                )
            expected_type = var_meta.get("type")
            if expected_type and var_name in kwargs:
                type_map = {"str": str, "int": int, "float": float, "bool": bool}
                py_type = type_map.get(expected_type)
                if py_type and not isinstance(kwargs[var_name], py_type):
                    raise TypeError(
                        f"[promptvault] Variable '{var_name}' in prompt '{self.name}' "
                        f"expected {expected_type}, got {type(kwargs[var_name]).__name__}."
                    )

    def _apply_defaults(self, kwargs: dict) -> dict:
        merged = {}
        for var_name, var_meta in self.variables.items():
            if var_name in kwargs:
                merged[var_name] = kwargs[var_name]
            elif "default" in var_meta:
                merged[var_name] = var_meta["default"]
        merged.update({k: v for k, v in kwargs.items() if k not in merged})
        return merged

    def __repr__(self) -> str:
        return f"Prompt(name={self.name!r}, version={self.version!r})"
