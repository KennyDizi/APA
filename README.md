<div align="center">

# 🚀 APA – Async Prompt Optimizer

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with LiteLLM](https://img.shields.io/badge/built%20with-LiteLLM-orange.svg)](https://github.com/BerriAI/litellm)

**Transform plain text into powerful AI prompts with async efficiency**

APA is an **async, provider-agnostic** command-line tool that converts `.txt` files into structured prompts for leading LLM providers. Built on [LiteLLM](https://github.com/BerriAI/litellm) with enterprise-grade retry logic and clean architecture.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [API](#-api) • [Contributing](#-contributing)

</div>

---

## ✨ Features

<table>
<tr>
<td>

### 🔌 Universal Provider Support
- OpenAI (GPT-4, o3, o4)
- Anthropic (Claude 3.7, Sonnet 4, Opus 4)
- DeepSeek
- OpenRouter

</td>
<td>

### ⚡ Performance & Reliability
- Fully async architecture
- Real-time streaming support
- Auto-retry with exponential backoff
- Concurrent request handling

</td>
</tr>
<tr>
<td>

### 🧠 Smart Model Features
- `reasoning_effort` for OpenAI o3/o4
- Extended thinking tokens for Claude
- Auto-detect model capabilities
- Developer role injection

</td>
<td>

### 🛠️ Developer Experience
- Clean architecture design
- TOML-based configuration
- Environment variable support
- Library-ready API

</td>
</tr>
</table>

---

## 📁 Project Structure

```
apa/
├── 📄 configuration.toml      # Runtime settings
├── 📄 system_prompt.toml      # Customizable system prompt
├── 🐍 __init__.py
├── 🔧 config.py               # Unified configuration system
├── 📂 domain/                 # Domain layer
│   ├── models.py              # Value objects (Prompt, LLMConfig, etc.)
│   ├── interfaces.py          # Abstract interfaces
│   └── exceptions.py          # Domain exceptions
├── 📂 application/            # Application layer
│   ├── prompt_processor.py    # Prompt processing orchestration
│   └── response_handler.py    # Response handling and file output
└── 📂 infrastructure/         # Infrastructure layer
    ├── llm/
    │   ├── llm_client.py       # LiteLLM adapter
    │   └── model_capabilities.py # Model capability definitions
    ├── io/
    │   └── file_writer.py      # File I/O operations
    └── ui/
        └── console_loading_indicator.py # Loading animations
📄 main.py                     # CLI entry point
🚀 run-apa.sh                  # uv-powered execution script
📋 requirements.txt            # Dependencies
📦 pyproject.toml              # Project metadata
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.13+** 
- **API Key** for at least one provider
- **[uv](https://github.com/astral-sh/uv)** (recommended) or pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/apa.git
cd apa

# 2. Create virtual environment
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install APA
uv pip install -e .

# 4. Set up your API key
echo "OPENAI_API_KEY=sk-..." > .env
```

---

## 🎯 Usage

### Command Line

Create a prompt file:
```bash
echo "Explain quantum computing in simple terms" > prompt.txt
```

Run APA:
```bash
# Using the helper script (auto-loads .env, manages virtual environment with uv)
./run-apa.sh --msg-file prompt.txt

# Direct execution
python main.py --msg-file prompt.txt

# After installation
apa --msg-file prompt.txt
```

### 📚 As a Library

```python
import asyncio
from apa.config import load_settings
from apa.domain.models import Prompt, SystemPrompt, LLMConfig
from apa.application.prompt_processor import PromptProcessor
from apa.infrastructure.llm.llm_client import LLMClient

async def main():
    # Load unified configuration
    settings = load_settings()
    
    # Create domain objects
    user_prompt = Prompt(content="Explain the SOLID principles", language=settings.programming_language)
    system_prompt = SystemPrompt(template=settings.system_prompt, language=settings.programming_language)
    
    llm_config = LLMConfig(
        provider=settings.provider,
        model=settings.model,
        api_key=settings.api_key,
        temperature=settings.temperature,
        stream=settings.stream
    )
    
    # Create infrastructure and application services
    llm_client = LLMClient(llm_config)
    prompt_processor = PromptProcessor(llm_client)
    
    # Process prompt
    if settings.stream:
        async for chunk in prompt_processor.process_prompt_stream(system_prompt, user_prompt, llm_config):
            print(chunk, end='', flush=True)
    else:
        response = await prompt_processor.process_prompt(system_prompt, user_prompt, llm_config)
        print(response)

asyncio.run(main())
```

---

## ⚙️ Configuration

### 📄 `apa/configuration.toml`

```toml
# Model parameters
temperature      = 0.2           # Creativity level (0.0-1.0)
stream           = true          # Enable real-time streaming

# Provider-specific settings
programming_language = "Python"  # Default language injected into system prompt
reasoning_effort = "high"        # OpenAI o3/o4 models only
thinking_tokens  = 16384         # Anthropic Claude models only

# Model selection
provider = "openai"              # openai | anthropic | deepseek | openrouter
model    = "o3"                  # Model identifier

# Fallback configuration (optional)
fallback_provider = "anthropic"  # Provider to use if primary fails
fallback_model = "claude-sonnet-4-20250514"  # Model to use if primary fails
```

### 🤖 `apa/system_prompt.toml` (templated)

Customize the AI assistant's behavior:
```toml
system_prompt = """
## Role
You are an advanced AI programming assistant specializing in $programming_language programming language...

## Task
Your tasks include...
"""
```
```

The only variable required is `programming_language`. The value comes from `configuration.toml`; if omitted it defaults to "Python".


### 🔐 Environment Variables

Create a `.env` file:
```bash
# Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=anthropic-...
DEEPSEEK_API_KEY=...
OPENROUTER_API_KEY=...
```

---

## 🔧 Advanced Features

### Model Capabilities

| Feature | Supported Models |
|---------|-----------------|
| 🎯 Reasoning Effort | o3, o3-mini, o4, o4-mini |
| 🧠 Extended Thinking | Claude 3.7 Sonnet, Sonnet 4, Opus 4 |
| 👨‍💻 Developer Role | o1, o3, o4, gpt-4.1 |
| 🌡️ No Temperature | DeepSeek Reasoner, o1-o4 series |

### Retry Configuration

APA automatically retries failed requests:
- **3 attempts** maximum
- **Exponential backoff**: 2-8 seconds
- **Smart error handling**

### Fallback Mechanism

APA includes an intelligent fallback system that automatically switches providers when the primary fails:

- **Primary attempts**: 3 tries with exponential backoff
- **Automatic switchover**: Seamlessly transitions to fallback provider
- **Provider hot-swap**: Loads provider-specific settings without restart
- **Configurable**: Set `fallback_provider` and `fallback_model` in `configuration.toml`

To disable fallback, simply omit these keys from your configuration.

Example configuration:
```toml
# Primary provider
provider = "openai"
model = "gpt-4"

# Fallback provider (activated after 3 primary failures)
fallback_provider = "anthropic"
fallback_model = "claude-sonnet-4-20250514"
```

---

## 🤝 Contributing

### Adding a New Provider

1. Update `PROVIDER_ENV_MAP` in `apa/config.py`
2. Add model capabilities to `apa/infrastructure/llm/model_capabilities.py`
3. Update LLMClient logic if needed
4. Test with your API key

### Architecture

APA follows Clean Architecture principles with clear separation of concerns:

- **Domain Layer**: Core business logic and value objects
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External adapters (LLM providers, file I/O, UI)

The unified configuration system in `apa/config.py` provides a single entry point for all settings with automatic provider detection and template rendering.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by [Kenny Dizi](https://github.com/KennyDizi)**

[Report Bug](https://github.com/KennyDizi/apa/issues) • [Request Feature](https://github.com/KennyDizi/apa/issues)

</div>
