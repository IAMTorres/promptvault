"""
Team workflow example — shows version management, A/B testing and diffs.

This is the core use case: a team is iterating on prompts and needs to
track what changed, compare versions and roll back when output degrades.
"""

from promptvault import PromptVault

vault = PromptVault("./prompts")

# ── Scenario: the summarize prompt was updated, output got worse ───────────────

# Load v1.0 (original, working well in January)
v1 = vault.load("summarize", version="1.0")

# Load v1.1 (updated in March, output degraded)
v2 = vault.load("summarize", version="1.1")

print(f"Loaded: {v1.name} v{v1.version} by {v1.author}")
print(f"Loaded: {v2.name} v{v2.version} by {v2.author}")

# ── See exactly what changed ───────────────────────────────────────────────────
print("\n--- Diff between v1.0 and v1.1 ---")
print(vault.diff("summarize", "1.0", "1.1"))

# ── A/B test: send the same text through both versions ────────────────────────
article = """
The Portuguese startup ecosystem has grown significantly in the past five years,
with Lisbon becoming one of Europe's top tech hubs. Funding rounds have increased,
and several unicorns have emerged. The government has supported this growth through
favourable tax policies and the golden visa programme.
"""

rendered_v1 = v1.render(text=article, max_words=40)
rendered_v2 = v2.render(text=article, max_words=40)

print("\n--- v1.0 rendered prompt ---")
print(rendered_v1)

print("\n--- v1.1 rendered prompt ---")
print(rendered_v2)

# In production you'd send both to your LLM and compare outputs.
# When v1.1 performs worse, you roll back by switching version="1.0".

# ── List all versions ──────────────────────────────────────────────────────────
print("\nAll versions of 'summarize':", vault.versions("summarize"))
print("All prompts in vault:", vault.list())
