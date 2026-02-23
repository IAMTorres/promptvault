# promptvault

Manage, version and log your LLM prompts as plain YAML files — tracked by git, loaded in one line.

**Created by [Gonçalo Torres](https://github.com/IAMTorres)**

---

## The problem

Every developer building with LLMs has prompts scattered across the codebase as hardcoded strings:

```python
# Somewhere in your code...
response = client.chat("Summarize in 100 words: " + text)

# Somewhere else...
response = client.chat("Extract JSON from: " + text)

# Another file...
response = client.chat("You are a helpful assistant that...")
```

When output quality drops, you don't know which prompt changed, when, or why.
When you're in a team, there's no way to collaborate on prompts.
When you want to test two versions, you duplicate code.

**promptvault** fixes this by treating prompts as first-class artifacts — versioned files, loaded by name, tracked by git.

---

## Installation

```bash
pip install promptvault
```

---

## Quick Start

**1. Create a prompt file** (`prompts/summarize.yaml`):

```yaml
name: summarize
version: "1.0"
description: Summarize text to a given word count.
author: your-name

template: |
  Summarize the following text in $max_words words or fewer.
  Focus only on key points. Return only the summary.

  Text:
  $text

variables:
  text:
    type: str
    required: true
  max_words:
    type: int
    required: false
    default: 100
```

**2. Load and use it:**

```python
from promptvault import PromptVault

vault  = PromptVault("./prompts")
prompt = vault.load("summarize")
text   = prompt.render(text="Your article here...", max_words=50)

# Pass to any LLM
response = client.chat(text)
```

That's it. The prompt lives in a file, has a version, and can be tracked with git.

---

## API Reference

### `PromptVault(path, log_file=None)`

```python
vault = PromptVault("./prompts")                          # basic
vault = PromptVault("./prompts", log_file="usage.jsonl")  # with usage logging
```

| Parameter | Description |
|-----------|-------------|
| `path` | Directory containing your `.yaml` prompt files |
| `log_file` | Optional path to a `.jsonl` file for usage logging |

---

### `vault.load(name, version=None)`

Load a prompt by name. If `version` is omitted, loads the latest.

```python
prompt = vault.load("summarize")           # latest version
prompt = vault.load("summarize", version="1.0")  # specific version
```

---

### `prompt.render(**kwargs)`

Render the prompt template with variables.

```python
text = prompt.render(text="...", max_words=50)
```

- Missing required variables raise `KeyError`
- Wrong types raise `TypeError`
- Variables with defaults are optional

---

### `vault.list()`

Returns all prompt names in the vault.

```python
vault.list()
# ["classify", "code_review", "reply_email", "sql_query", "summarize"]
```

---

### `vault.versions(name)`

Returns all available versions for a prompt.

```python
vault.versions("summarize")
# ["1.0", "1.1", "1.2"]
```

---

### `vault.diff(name, version_a, version_b)`

Shows a unified diff between two versions of a prompt template.

```python
print(vault.diff("summarize", "1.0", "1.1"))
```

```diff
--- summarize v1.0
+++ summarize v1.1
@@ -1,4 +1,4 @@
-Summarize the following text in $max_words words or fewer.
-Focus only on the key points. Do not add opinions.
+Please summarize the text below.
+Try to keep it around $max_words words. Be helpful and include context.
```

---

### `vault.log(...)`

Append a usage record to a JSONL log file.

```python
vault.log(
    "summarize",
    version=prompt.version,
    rendered=rendered_text,
    response=llm_response,
    model="gpt-4o-mini",
)
```

Each log entry is one line of JSON:
```json
{"timestamp": "2025-03-15T14:22:01", "prompt": "summarize", "version": "1.0", "model": "gpt-4o-mini", "rendered": "...", "response": "..."}
```

---

## Prompt File Format

```yaml
name: my_prompt         # required — used to load by name
version: "1.0"          # required — semver string
description: ...        # optional
author: your-name       # optional
tags: [tag1, tag2]      # optional

template: |             # required — the actual prompt text
  Your prompt here with $variable placeholders.

variables:              # optional — describe and validate your variables
  variable_name:
    type: str           # str, int, float, bool
    required: true      # default: true
    default: value      # makes the variable optional
    description: ...
```

Templates use Python's `$variable` syntax (`string.Template`).

---

## Real-World Use Cases

### Summarisation — media, research, legal, finance

```yaml
name: summarize_legal
version: "1.0"
template: |
  Summarize the following legal document in plain language.
  Use $max_words words or fewer. Highlight obligations and deadlines.
  Return only the summary.

  Document:
  $text
```

### Customer support ticket classification

```yaml
name: classify_ticket
version: "1.0"
template: |
  Classify this support ticket into one category: $categories.
  Return only the category name.

  Ticket:
  $text
```

### Data extraction from unstructured text — CVs, invoices, emails

```yaml
name: extract_invoice
version: "1.0"
template: |
  Extract the following fields from this invoice and return a JSON object.
  If a field is missing, use null. Return only JSON.

  Fields: $fields

  Invoice text:
  $text
```

### SQL generation — internal tools, dashboards, BI

```yaml
name: nl_to_sql
version: "1.0"
template: |
  Generate a valid $dialect SQL query for the question below.
  Use only the tables and columns in the schema. Return only SQL.

  Schema:
  $schema

  Question:
  $question
```

### Code review automation — CI pipelines, PR bots

```yaml
name: code_review
version: "1.0"
template: |
  Review this $language code. Identify bugs, security issues and improvements.
  Format as a numbered list. If correct, say "No issues found."

  Code:
  $code
```

### Email drafting — sales, support, internal comms

```yaml
name: reply_email
version: "1.0"
template: |
  Write a $tone professional email reply in $max_lines lines or fewer.
  Address all points raised. Sign off with: $signature.

  Original email:
  $original_email

  Instructions:
  $context
```

---

## Team Workflow

### Why it matters in a team

When multiple people work on a product that uses LLMs, prompts get edited silently. Quality degrades and nobody knows why.

With promptvault and git, the workflow becomes:

```
# January — everything works well
prompts/summarize.yaml  (v1.0, by Alice)

# March — a colleague updates the prompt
prompts/summarize.yaml  (v1.1, by Bob)
# → git commit shows exactly what changed

# Output degrades
# → git log prompts/summarize.yaml
# → git diff / vault.diff()
# → roll back to v1.0 in one line
```

### Version in separate files or same file?

You can store multiple versions as separate files in the same folder:

```
prompts/
├── summarize.yaml          # version: "1.0"
├── summarize_v1_1.yaml     # version: "1.1"
└── summarize_v1_2.yaml     # version: "1.2"
```

`vault.load("summarize")` finds all files with `name: summarize` and returns the latest.
`vault.load("summarize", version="1.1")` returns the specific version.

---

## Works with Any LLM

promptvault is completely model-agnostic. It produces a rendered string — you pass it to whatever LLM client you use.

```python
# OpenAI
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt.render(**vars)}]
)

# Anthropic Claude
response = anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": prompt.render(**vars)}]
)

# Local LLM via Ollama
response = requests.post("http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt.render(**vars)})

# Azure OpenAI, Gemini, Mistral, Groq — same pattern
```

---

## Examples

| Example | What it shows |
|---------|---------------|
| `examples/basic/` | Load and render prompts without any LLM |
| `examples/openai_example/` | Summarise + extract JSON with OpenAI |
| `examples/anthropic_example/` | Code review + classify + SQL with Claude |
| `examples/team_workflow/` | Version diff and A/B testing between prompt versions |

---

## Author

**Gonçalo Torres** — [github.com/IAMTorres](https://github.com/IAMTorres)

## License

MIT
