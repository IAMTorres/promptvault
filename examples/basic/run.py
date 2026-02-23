"""
Basic example — load and render prompts without any LLM.
Shows the core promptvault API.
"""

from promptvault import PromptVault

vault = PromptVault("../../prompts")

# ── 1. List all available prompts ─────────────────────────────────────────────
print("Available prompts:", vault.list())

# ── 2. Load and render a prompt ────────────────────────────────────────────────
prompt = vault.load("summarize")
print(f"\nLoaded: {prompt.name} v{prompt.version}")
print(f"Description: {prompt.description}")

rendered = prompt.render(
    text="Python is a high-level programming language known for its simplicity.",
    max_words=30,
)
print("\nRendered prompt:")
print(rendered)

# ── 3. Use default variable values ─────────────────────────────────────────────
rendered_defaults = prompt.render(
    text="Python is a high-level programming language known for its simplicity.",
    # max_words not passed — defaults to 100
)
print("\nRendered with defaults (max_words=100):")
print(rendered_defaults)

# ── 4. Load a specific version ─────────────────────────────────────────────────
# prompt_v1 = vault.load("summarize", version="1.0")

# ── 5. List versions ───────────────────────────────────────────────────────────
print("\nVersions of 'summarize':", vault.versions("summarize"))
