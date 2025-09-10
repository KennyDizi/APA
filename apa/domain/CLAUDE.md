# CLAUDE.md - Domain Layer

This file provides guidance for working with the Domain layer in the APA Clean Architecture.

## Domain Layer Purpose

The Domain layer contains the core business logic and rules of the APA application. It should have NO dependencies on external frameworks, infrastructure, or UI concerns.

## Files Overview

### `models.py` - Value Objects
- **Prompt**: Immutable value object for user input with language specification
- **SystemPrompt**: Template-based system prompt with rendering capability  
- **LLMResponse**: Response data from LLM providers with metadata
- **LLMConfig**: Complete configuration for LLM requests including fallback settings

**Key Patterns:**
- All models use `@dataclass(frozen=True)` for immutability where appropriate
- Template rendering uses Python's `string.Template` with `safe_substitute()`
- Language defaults to "Python" if not specified

### `interfaces.py` - Abstract Contracts
- **LoadingIndicator**: Abstract interface for UI loading states
- Defines contracts that infrastructure layer must implement
- Uses ABC (Abstract Base Class) pattern

### `exceptions.py` - Domain Exceptions  
- **APAError**: Base exception for all application errors
- **ConfigurationError**: Configuration validation failures
- **ProviderError**: LLM provider communication issues
- **PromptProcessingError**: Prompt processing failures

## Domain Rules

### Value Object Construction
```python
# Correct: Immutable prompt creation
prompt = Prompt(content="user input", language="Python")

# Correct: System prompt with template
system_prompt = SystemPrompt(
    template="You are a $programming_language expert...",
    language="Python"
)
rendered = system_prompt.render(programming_language="Python")
```

### Configuration Object Pattern
```python
# Complete LLM configuration with all parameters
llm_config = LLMConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-...",
    temperature=0.7,
    reasoning_effort="high",
    thinking_tokens=16384,
    stream=False,
    programming_language="Python",
    fallback_provider="anthropic",
    fallback_model="claude-sonnet-4"
)
```

## Development Guidelines

### Adding New Value Objects
- Use `@dataclass` with appropriate `frozen=` setting
- Include comprehensive docstrings
- Ensure immutability for value objects
- Add validation in `__post_init__` if needed

### Exception Handling
- Always inherit from `APAError` for application exceptions
- Provide descriptive error messages
- Chain exceptions using `from e` to preserve stack traces

### Interface Design
- Keep interfaces minimal and focused
- Use ABC pattern with `@abstractmethod`
- Document expected behavior in docstrings

## Testing Considerations

When testing domain objects:
- Test immutability constraints
- Validate template rendering with various inputs
- Ensure exception messages are helpful
- Test edge cases for validation logic