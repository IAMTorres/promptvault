"""
OpenAI example — use promptvault with the OpenAI Python SDK.

Install: pip install openai promptvault
Set env: OPENAI_API_KEY=your-key
"""

import os
from openai import OpenAI
from promptvault import PromptVault

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
vault  = PromptVault("../../prompts", log_file="./usage.jsonl")

# ── Summarise a document ───────────────────────────────────────────────────────
article = """
The James Webb Space Telescope (JWST) has captured unprecedented images of the
early universe. Launched in December 2021, the telescope uses infrared light to
observe galaxies formed shortly after the Big Bang. Scientists have already
discovered galaxies older than previously thought possible, challenging existing
models of galaxy formation. The telescope's mirror, spanning 6.5 metres, allows
it to detect light from objects over 13 billion light-years away.
"""

prompt = vault.load("summarize")
rendered = prompt.render(text=article, max_words=50)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": rendered}],
)
result = response.choices[0].message.content

print("Summary:", result)

# Log the call for future reference
vault.log(
    "summarize",
    version=prompt.version,
    rendered=rendered,
    response=result,
    model="gpt-4o-mini",
)

# ── Extract structured data ────────────────────────────────────────────────────
import json

cv_text = """
John Smith — Software Engineer
Email: john@example.com | Phone: +351 912 345 678
Currently at Accenture Portugal since 2022.
Previously worked at NOS Comunicações (2019-2022).
"""

extract_prompt = vault.load("extract_json")
rendered = extract_prompt.render(
    text=cv_text,
    fields="name, email, phone, current_company, previous_company",
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": rendered}],
)
data = json.loads(response.choices[0].message.content)
print("\nExtracted:", data)

vault.log("extract_json", version=extract_prompt.version,
          rendered=rendered, response=str(data), model="gpt-4o-mini")
