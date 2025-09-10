# CLAUDE.md - LLM Infrastructure

This file provides guidance for working with LLM provider infrastructure in APA.

## Purpose

This directory contains all LLM provider integration logic, including the LiteLLM adapter and model capability management.

## Files Overview

### `llm_client.py` - LiteLLM Adapter
**Core responsibility**: Translate domain requests into LiteLLM API calls with model-specific parameter handling.

**Key Methods:**
- `generate_completion()`: Non-streaming LLM completion
- `generate_completion_stream()`: Streaming LLM completion  
- `_prepare_messages()`: Format messages with appropriate roles
- `_prepare_completion_kwargs()`: Build LiteLLM parameters
- `_add_temperature_config()`: Handle temperature parameter
- `_add_reasoning_effort_config()`: Handle OpenAI reasoning effort
- `_add_thinking_tokens_config()`: Handle Anthropic thinking tokens

**Critical Implementation Details:**
- Uses model capability detection to determine which parameters to send
- Handles provider-specific parameter formatting
- Translates LiteLLM exceptions to domain exceptions
- Supports both streaming and non-streaming modes

### `model_capabilities.py` - Model Capability Definitions  
**Core responsibility**: Centralized model capability definitions that determine API parameter inclusion.

**Capability Sets:**
- `NO_SUPPORT_TEMPERATURE_MODELS`: Models that reject temperature parameter
- `SUPPORT_REASONING_EFFORT_MODELS`: OpenAI models supporting reasoning_effort
- `SUPPORT_DEVELOPER_MESSAGE_MODELS`: Models using "developer" role vs "system" 
- `EXTENDED_THINKING_MODELS`: Anthropic models supporting thinking token budgets
- `REASONING_EFFORT_SUPPORTED_PROVIDERS`: Providers supporting reasoning_effort parameter

## Model Capability System

### How It Works
The capability system prevents API errors by only sending parameters that models support:

```python
# Only send temperature if model supports it
if model not in NO_SUPPORT_TEMPERATURE_MODELS and temperature is not None:
    kwargs["temperature"] = temperature

# Only send reasoning_effort for compatible models AND providers
if (model in SUPPORT_REASONING_EFFORT_MODELS and
    self.config.provider in REASONING_EFFORT_SUPPORTED_PROVIDERS and
    self.config.reasoning_effort):
    kwargs["reasoning_effort"] = self.config.reasoning_effort
```

### Adding New Model Capabilities
1. Add model identifier to appropriate frozenset in `model_capabilities.py`
2. Update parameter logic in `llm_client.py` if needed
3. Test with actual API calls

Example:
```python
# Add to model_capabilities.py
SUPPORT_REASONING_EFFORT_MODELS = frozenset({
    "o3-mini",
    "new-reasoning-model",  # Add here
    # ... existing models
})
```

## LiteLLM Integration Patterns

### Provider-Specific Formatting
```python
# Model name formatting
"model": f"{self.config.provider}/{model}"

# Provider-specific parameters
if self.config.provider in self.REASONING_EFFORT_SUPPORTED_PROVIDERS:
    kwargs["reasoning_effort"] = self.config.reasoning_effort
    kwargs["allowed_openai_params"] = ["reasoning_effort"]
```

### Message Role Handling
```python
# Some models use "developer" role instead of "system"
role = "developer" if model in SUPPORT_DEVELOPER_MESSAGE_MODELS else "system"
messages = [
    {"role": role, "content": system_prompt},
    {"role": "user", "content": user_prompt}
]
```

### Streaming Response Handling  
```python
async def generate_completion_stream(self):
    response = await litellm.acompletion(**kwargs)
    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## Development Guidelines

### Adding New Providers
1. Update `apa/config.py` with provider environment mapping
2. Add provider to `REASONING_EFFORT_SUPPORTED_PROVIDERS` if applicable
3. Update model capability sets with provider-specific model names
4. Test provider-specific parameter handling

### Adding New Model Parameters
1. Check provider documentation for parameter support
2. Add capability detection in `model_capabilities.py`
3. Implement parameter logic in `_prepare_completion_kwargs()`
4. Create helper method like `_add_new_param_config()` for complex logic
5. Test with models that support and don't support the parameter

### Error Handling Patterns
```python
try:
    response = await litellm.acompletion(**kwargs)
    # Process response
except Exception as e:
    # Always translate to domain exception
    raise ProviderError(f"LLM provider failed: {str(e)}") from e
```

## Model-Specific Considerations

### OpenAI Models (o1, o3, o4 series)
- Don't support temperature parameter
- Support reasoning_effort (o3, o4 only)
- Some use "developer" message role
- Require specific allowed_openai_params for reasoning_effort

### Anthropic Models (Claude series) 
- Support thinking token budgets
- Use standard message roles
- Support temperature parameter
- Thinking tokens force temperature to 1.0

### DeepSeek Models
- Limited parameter support
- Special handling for DeepSeek Reasoner

## Testing LLM Infrastructure

### Unit Testing
- Mock LiteLLM responses
- Test capability-based parameter inclusion/exclusion
- Verify exception translation
- Test message formatting for different models

### Integration Testing
- Test with real API keys in development
- Verify parameter handling with actual providers
- Test streaming response handling
- Validate error scenarios with invalid parameters