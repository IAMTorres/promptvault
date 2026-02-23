"""
Anthropic (Claude) example — use promptvault with the Anthropic Python SDK.

Install: pip install anthropic promptvault
Set env: ANTHROPIC_API_KEY=your-key
"""

import os
import json
from anthropic import Anthropic
from promptvault import PromptVault

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
vault  = PromptVault("../../prompts", log_file="./usage.jsonl")

# ── Code review ────────────────────────────────────────────────────────────────
code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    result = db.execute(query)
    return result[0]
"""

prompt  = vault.load("code_review")
rendered = prompt.render(code=code, language="python")

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{"role": "user", "content": rendered}],
)
review = response.content[0].text
print("Code review:\n", review)

vault.log("code_review", version=prompt.version,
          rendered=rendered, response=review, model="claude-haiku-4-5-20251001")

# ── Classify customer support ticket ──────────────────────────────────────────
ticket = "My order arrived broken. The screen is completely shattered. I want a refund."

classify_prompt = vault.load("classify")
rendered = classify_prompt.render(
    text=ticket,
    categories="refund_request, delivery_issue, technical_support, billing, general_inquiry",
)

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=32,
    messages=[{"role": "user", "content": rendered}],
)
category = response.content[0].text.strip()
print(f"\nTicket category: {category}")

vault.log("classify", version=classify_prompt.version,
          rendered=rendered, response=category, model="claude-haiku-4-5-20251001")

# ── Generate SQL from natural language ─────────────────────────────────────────
schema = """
users(id INT, name VARCHAR, email VARCHAR, plan VARCHAR, created_at TIMESTAMP)
subscriptions(id INT, user_id INT, plan VARCHAR, start_date DATE, end_date DATE, active BOOL)
payments(id INT, user_id INT, amount DECIMAL, paid_at TIMESTAMP, status VARCHAR)
"""

question = "How many active users are on the pro plan and paid more than 100 euros last month?"

sql_prompt = vault.load("sql_query")
rendered   = sql_prompt.render(schema=schema, question=question, dialect="PostgreSQL")

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{"role": "user", "content": rendered}],
)
sql = response.content[0].text.strip()
print(f"\nGenerated SQL:\n{sql}")
