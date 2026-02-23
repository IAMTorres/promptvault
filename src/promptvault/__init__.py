"""
promptvault — Manage, version and log LLM prompts as plain YAML files.

    from promptvault import PromptVault

    vault = PromptVault("./prompts")
    prompt = vault.load("summarize")
    text   = prompt.render(text="...", max_words=100)

"""

from .prompt import Prompt
from .vault import PromptVault

__all__ = ["PromptVault", "Prompt"]
__version__ = "1.0.0"
