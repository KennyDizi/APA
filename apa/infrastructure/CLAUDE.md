# CLAUDE.md - Infrastructure Layer

This file provides guidance for working with the Infrastructure layer in the APA Clean Architecture.

## Infrastructure Layer Purpose

The Infrastructure layer contains all external concerns: APIs, databases, file systems, UI components, and third-party services. This layer implements interfaces defined in the Domain layer.

## Layer Structure

### `llm/` - LLM Provider Adapters
- **`llm_client.py`**: LiteLLM adapter with model capability detection
- **`model_capabilities.py`**: Centralized model capability definitions

### `io/` - File System Operations  
- **`file_writer.py`**: File writing operations with proper encoding

### `ui/` - User Interface Components
- **`console_loading_indicator.py`**: Terminal loading animations

## Key Infrastructure Patterns

### Adapter Pattern
Infrastructure components adapt external services to domain interfaces:
```python
class LLMClient:
    """Adapter for interacting with LLM providers through LiteLLM."""
    
    def __init__(self, config: LLMConfig):
        self.config = config  # Domain object
```

### Capability-Based Configuration
Model capabilities determine which parameters to send:
```python
# Temperature handling based on model capability
if model not in NO_SUPPORT_TEMPERATURE_MODELS and temperature is not None:
    kwargs["temperature"] = temperature
```

### Exception Translation
Infrastructure exceptions are translated to domain exceptions:
```python
except Exception as e:
    raise ProviderError(f"LLM provider failed: {str(e)}") from e
```

## Development Guidelines

### Adding New Infrastructure Components
1. Implement domain interfaces where applicable
2. Accept domain objects as parameters
3. Translate exceptions to domain exceptions
4. Handle external service specifics internally
5. Use dependency injection patterns

### External Service Integration
- Always wrap external libraries (LiteLLM, file operations, etc.)
- Provide abstractions that hide external service details
- Handle service-specific errors and translate them
- Make external dependencies configurable

### Configuration Management
- Accept configuration through domain objects
- Validate external service requirements
- Provide clear error messages for configuration issues

## Testing Infrastructure

### Unit Testing Strategy
- Mock external services
- Test error handling and exception translation
- Verify configuration parameter handling
- Test capability-based logic

### Integration Testing
- Test with real external services in development
- Verify proper error propagation
- Test timeout and retry behaviors
- Validate output formats

## Subdirectory Guidelines

Each subdirectory has its own specialized CLAUDE.md with detailed guidance:

- **`llm/CLAUDE.md`**: LLM provider integration patterns
- **`io/CLAUDE.md`**: File system operation guidelines  
- **`ui/CLAUDE.md`**: User interface component patterns

## Common Infrastructure Concerns

### Error Handling
- Always translate external exceptions
- Preserve original error context
- Provide meaningful error messages
- Log errors at appropriate levels

### Resource Management
- Properly close connections and files
- Handle timeouts appropriately
- Implement retry logic where beneficial
- Clean up resources in error scenarios

### Performance Considerations
- Use async operations where possible
- Implement appropriate timeouts
- Consider caching where beneficial
- Handle large responses efficiently