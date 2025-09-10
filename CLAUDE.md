# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

APA (Async Prompt Application) is an async, provider-agnostic CLI tool for converting text files into structured prompts for LLM providers. Built with Clean Architecture principles and powered by LiteLLM.

## Essential Commands

### Development Setup
```bash
# Setup with uv (recommended)
uv venv .venv && source .venv/bin/activate
uv pip install -e .

# Environment setup
echo "OPENAI_API_KEY=sk-..." > .env
```

### Running the Application
```bash
# Using the shell script (auto-loads .env)
./run-apa.sh --msg-file prompts.txt

# Direct execution
python main.py --msg-file prompts.txt

# After installation
apa --msg-file prompts.txt
```

### Testing & Validation
```bash
# Test configuration loading
python -c "from apa.config import load_settings; load_settings()"

# Test imports
python -c "from apa.infrastructure.llm.llm_client import LLMClient"

# Syntax check
python -m py_compile main.py
find apa/ -name "*.py" -exec python -m py_compile {} \;
```

## Architecture

### Clean Architecture Layers

**Domain Layer** (`apa/domain/`)
- `models.py`: Core value objects (Prompt, SystemPrompt, LLMConfig, LLMResponse) 
- `interfaces.py`: Abstract interfaces (LoadingIndicator)
- `exceptions.py`: Domain exceptions (APAError, ConfigurationError, ProviderError, PromptProcessingError)

**Application Layer** (`apa/application/`)  
- `prompt_processor.py`: Orchestrates prompt processing with loading indicators and streaming
- `response_handler.py`: Handles LLM responses and generates timestamped output files

**Infrastructure Layer** (`apa/infrastructure/`)
- `llm/llm_client.py`: LiteLLM adapter with model capability detection and parameter handling
- `llm/model_capabilities.py`: Centralized model capability definitions (temperature support, reasoning effort, developer messages, thinking tokens)  
- `io/file_writer.py`: File I/O operations
- `ui/console_loading_indicator.py`: Console UI for loading states

**Configuration** (`apa/config.py`)
- Single unified configuration system using `load_settings()`
- Auto-detects providers from environment variables
- Template rendering for system prompts
- Provider/API key resolution logic

### Key Design Patterns

**Provider Auto-Detection**: Configuration automatically detects available API keys and sets provider accordingly.

**Model Capability System**: Centralized capability definitions that determine which parameters to send based on model type:
- Temperature support detection
- Reasoning effort for OpenAI o3/o4 models  
- Extended thinking tokens for Claude models
- Developer message role injection

**Fallback Mechanism**: Primary provider attempts with automatic switchover to fallback provider on failure.

**Streaming Support**: Both streaming and non-streaming completions with proper loading indicator management.

## Configuration System

### Files
- `apa/configuration.toml`: Runtime settings (model, provider, parameters)
- `apa/system_prompt.toml`: Templated system prompt with `$programming_language` substitution
- `.env`: API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

### Key Configuration Logic
The `load_settings()` function in `apa/config.py`:
1. Loads TOML configuration 
2. Validates provider support
3. Auto-detects provider from environment variables
4. Loads and renders system prompt template
5. Returns unified Settings dataclass

### Provider Environment Mapping
```python
PROVIDER_ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY", 
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY"
}
```

## Model Capabilities

Located in `apa/infrastructure/llm/model_capabilities.py`, this module defines which models support specific features:

- `NO_SUPPORT_TEMPERATURE_MODELS`: Models that don't accept temperature parameter
- `SUPPORT_REASONING_EFFORT_MODELS`: OpenAI models supporting reasoning_effort
- `SUPPORT_DEVELOPER_MESSAGE_MODELS`: Models using "developer" role instead of "system"
- `EXTENDED_THINKING_MODELS`: Anthropic models supporting thinking token budgets

## Library Usage Pattern

The application can be used as a library through the config system:

```python
from apa.config import load_settings
settings = load_settings()  # Returns Settings dataclass with all configuration
```

This provides access to:
- `settings.system_prompt` (rendered template)
- `settings.provider`, `settings.api_key` 
- `settings.model`, `settings.temperature`
- All other configuration parameters

## Error Handling

Custom exception hierarchy:
- `APAError`: Base exception
- `ConfigurationError`: Configuration issues  
- `ProviderError`: LLM provider failures
- `PromptProcessingError`: Processing failures

All exceptions include descriptive error messages for debugging.

## Development Notes

- Python 3.13+ required
- Uses asyncio throughout for performance
- LiteLLM handles provider abstraction
- Clean separation between domain logic and infrastructure
- Configuration system was recently refactored to eliminate duplication (single `load_settings()` approach)