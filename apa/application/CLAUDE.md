# CLAUDE.md - Application Layer

This file provides guidance for working with the Application layer in the APA Clean Architecture.

## Application Layer Purpose

The Application layer orchestrates business workflows and use cases. It coordinates between the Domain and Infrastructure layers without containing business logic itself.

## Files Overview

### `prompt_processor.py` - Core Use Case
**Primary responsibility**: Orchestrate the prompt processing workflow

**Key Features:**
- Manages loading indicator lifecycle (start/stop)
- Handles both streaming and non-streaming responses
- Proper exception handling and cleanup
- Template rendering coordination

**Methods:**
- `process_prompt()`: Non-streaming LLM completion
- `process_prompt_stream()`: Streaming LLM completion with proper chunk handling

**Critical Implementation Details:**
- Loading indicator starts before LLM call, stops on first chunk in streaming mode
- Handles empty response from LLM as specific error case
- Ensures loading indicator cleanup in all exception scenarios
- Uses `__anext__()` pattern for proper async generator handling

### `response_handler.py` - Response Processing
**Primary responsibility**: Handle LLM response output and file management

**Key Features:**
- Generates timestamped filenames with format: `DD-MM-YYYY-HH-MM-AM/PM.txt`
- Handles file writing through FileWriter abstraction
- Proper error handling and exception propagation

**Filename Format Logic:**
- Converts 24-hour to 12-hour format
- Zero-pads day/month/hour/minute
- Handles midnight (00:00) as 12:00 AM correctly

## Application Service Patterns

### Dependency Injection
```python
class PromptProcessor:
    def __init__(self, llm_client, loading_indicator: Optional[LoadingIndicator] = None):
        self.llm_client = llm_client  # Infrastructure dependency
        self.loading_indicator = loading_indicator  # UI dependency
```

### Async Workflow Management
```python
async def process_prompt_stream(self, system_prompt, user_prompt, llm_config):
    try:
        if self.loading_indicator:
            self.loading_indicator.start()
        
        # Critical: Handle first chunk separately to stop loading indicator
        first_chunk = await stream.__anext__()
        if self.loading_indicator:
            self.loading_indicator.stop()
        yield first_chunk
        
        # Continue with remaining chunks
        async for chunk in stream:
            yield chunk
    except Exception as e:
        # Always cleanup loading indicator
        if self.loading_indicator:
            self.loading_indicator.stop()
        raise PromptProcessingError(f"Failed: {str(e)}") from e
```

### Exception Translation
Application services translate infrastructure exceptions into domain exceptions:
```python
except Exception as e:
    raise PromptProcessingError(f"Failed to process prompt: {str(e)}") from e
```

## Development Guidelines

### Adding New Use Cases
1. Create new application service class
2. Accept infrastructure dependencies via constructor
3. Coordinate workflow between domain and infrastructure
4. Translate exceptions to domain exceptions
5. Handle async operations properly

### Error Handling Patterns
- Always use `try/finally` or `try/except/finally` for cleanup
- Translate infrastructure exceptions to domain exceptions
- Preserve original exception context with `from e`
- Ensure proper resource cleanup (loading indicators, connections, etc.)

### Async Best Practices
- Use `async for` with proper exception handling
- Handle empty async generators explicitly
- Clean up resources in all code paths
- Use `__anext__()` when you need to handle first iteration differently

## Testing Application Services

### Unit Testing Focus
- Mock infrastructure dependencies
- Test workflow orchestration
- Verify exception translation
- Ensure proper cleanup in error scenarios

### Key Test Scenarios
- Successful completion (streaming and non-streaming)
- Empty response handling
- Exception propagation and translation
- Loading indicator lifecycle
- Resource cleanup in error cases

## Integration Points

### With Domain Layer
- Uses domain models (`Prompt`, `SystemPrompt`, `LLMConfig`)
- Throws domain exceptions (`PromptProcessingError`)
- Follows domain business rules

### With Infrastructure Layer
- Accepts infrastructure services via dependency injection
- Calls infrastructure methods (LLM client, file writer)
- Does not know about specific implementations