# APA – Async Prompt Application

APA is an **async, provider-agnostic** command–line tool that turns a plain
`.txt` file into a structured prompt for large-language-model back-ends such as
OpenAI, Anthropic, DeepSeek or OpenRouter.  
It is built on top of **[LiteLLM](https://github.com/BerriAI/litellm)**, uses
**tenacity** for retry/back-off and follows a lightweight Clean Architecture
layout for easy maintenance and extension.

---

## Features

* 🔌  Pluggable provider support (`openai`, `anthropic`, `deepseek`, `openrouter`)
* ⚡  Fully **async**; optional incremental streaming (`--stream` / `stream=true`)
* 🔄  Automatic retry with exponential back-off (3 attempts)
* 🤔  Provider-specific tweaks
  * `reasoning_effort` for OpenAI *o3 / o4* reasoning models  
  * Extended **Claude "thinking"** tokens for Anthropic models
  * Temperature automatically omitted for models that ignore it
* 🧑‍💻  `developer` role injection for models that support it
* 🗄️  Clear configuration via TOML + environment variables
* 🧪  Easy to embed as a library (`from apa.services import acompletion`)

---

## Directory layout

```
apa/
├── configuration.toml        # runtime settings
├── system_prompt.toml        # long, multi-line system prompt
├── __init__.py
├── config.py                 # config loader / env detection
├── infrastructure/
│   └── llm_client.py         # async wrapper around LiteLLM
└── services/
    └── __init__.py           # service façade (exports acompletion)
main.py                       # CLI entry-point (also exposed as `apa`)
run.sh                        # helper script that sources .env then runs main
requirements.txt              # pinned dependencies
pyproject.toml                # PEP-621 project + build metadata
```

---

## Requirements

* Python **3.13+**
* A valid LLM API key for at least one provider
  (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`)
* Recommended package manager: **[uv](https://github.com/astral-sh/uv)**

---

## Installation

### 1. Create and activate a virtual-env

```bash
uv venv .venv          # or python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
# Editable install (preferred when hacking on the code-base)
uv pip install -e .
# or strict, pinned versions:
uv pip install -r requirements.txt
```

---

## Configuration

### `apa/configuration.toml`

```toml
temperature      = 0.2           # default temp (ignored by some models)
stream           = false         # true = incremental output
reasoning_effort = "high"        # open-ai reasoning models
thinking_tokens  = 16384         # anthropic Claude models
provider         = "openai"      # openai | anthropic | deepseek | openrouter
model            = "o3"          # final model name to send to LiteLLM
```

### `apa/system_prompt.toml`

Contains a rich, multi-line prompt that defines the assistant's role,
workflow, output format and a "Questions for Clarification" section.
Feel free to tailor it to your own style; **no code changes are required**.

### `.env`

Store secrets here (sourced automatically by `run.sh`):

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
```

---

## Usage

### 1. Prepare a user message

```text
# prompt.txt
Rewrite the following Python loop using list-comprehension.
```

### 2. Run the tool

```bash
# via helper script (reads .env automatically)
./run.sh --msg-file prompt.txt

# or directly
python main.py --msg-file prompt.txt                # obeys stream flag in config
python main.py --msg-file prompt.txt --stream       # force streaming
# once installed
apa --msg-file prompt.txt
```

Streaming mode prints chunks as they arrive; non-streaming waits for the full
response and prints it once.

---

## Library example

```python
import asyncio
from apa.services import acompletion
from apa.config   import load_settings

cfg   = load_settings()
reply = asyncio.run(
    acompletion(
        cfg.system_prompt,
        "Summarise the SOLID principles.",
        model=cfg.model,
        stream=False,
    )
)
print(reply)
```

---

## Extending

* **Add a new provider** – update `PROVIDER_ENV_MAP` in `apa/config.py` and
  (optionally) extend the model-capability lists in `llm_client.py`.
* **Custom retry policy** – tweak the `@retry` decorator parameters.
* **Alternative front-ends** – re-use `apa.services.acompletion` in a FastAPI or
  Django view without touching low-level details.

---

## License

See [LICENSE](LICENSE) for full text. © 2025 Kenny Dizi.
