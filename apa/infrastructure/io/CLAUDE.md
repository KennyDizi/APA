# CLAUDE.md - I/O Infrastructure

This file provides guidance for working with file system operations in APA.

## Purpose

This directory contains all file system interaction logic, providing abstractions over file operations.

## Files Overview

### `file_writer.py` - File System Adapter
**Core responsibility**: Provide safe, consistent file writing operations with proper error handling.

**Key Features:**
- Pathlib-based file operations for cross-platform compatibility
- Configurable encoding and write modes
- Exception translation to domain exceptions
- Returns Path object for further operations

**Method Signature:**
```python
def write(
    self, 
    filename: str,
    content: str, 
    encoding: Optional[str] = None,
    mode: str = "w"
) -> Path
```

## File Operation Patterns

### Safe File Writing
```python
try:
    file_path = Path(filename)
    with file_path.open(mode=mode, encoding=encoding) as f:
        f.write(content)
    return file_path
except Exception as e:
    raise APAError(f"Failed to write to file {filename}: {str(e)}") from e
```

### Path Handling
- Uses `pathlib.Path` for modern path handling
- Returns Path object for chaining operations
- Cross-platform path resolution

## Usage Patterns

### Basic File Writing
```python
file_writer = FileWriter()
output_path = file_writer.write("response.txt", content, encoding="utf-8")
print(f"Written to: {output_path}")
```

### Custom Encoding and Mode
```python
# Append mode with specific encoding
file_writer.write("log.txt", log_content, encoding="utf-8", mode="a")

# Binary mode (when content is bytes, adjust signature accordingly)
file_writer.write("data.bin", binary_data, mode="wb")
```

## Development Guidelines

### Adding New File Operations
When adding new file operation methods:

1. **Use pathlib**: Always use `pathlib.Path` for path operations
2. **Exception Translation**: Translate filesystem exceptions to `APAError`
3. **Resource Management**: Use context managers (`with` statements) for file operations
4. **Return Paths**: Return `Path` objects for method chaining
5. **Encoding Awareness**: Always consider encoding for text operations

### Example New Method:
```python
def read(self, filename: str, encoding: Optional[str] = None) -> str:
    """Read content from a file."""
    try:
        file_path = Path(filename)
        if not file_path.exists():
            raise APAError(f"File does not exist: {filename}")
        
        with file_path.open(mode="r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise APAError(f"Failed to read from file {filename}: {str(e)}") from e
```

### Error Handling Patterns
- Always catch broad `Exception` for filesystem operations
- Provide descriptive error messages including filename
- Use `from e` to preserve original exception context
- Translate all exceptions to `APAError` or appropriate domain exception

### Encoding Considerations
- Default encoding should be explicit (usually "utf-8")
- Allow encoding override for different file types
- Consider BOM handling for text files when needed

## File System Best Practices

### Path Safety
```python
# Resolve paths safely
file_path = Path(filename).resolve()

# Check for directory traversal attacks if accepting user input
if not file_path.is_relative_to(safe_directory):
    raise APAError("Path traversal attempt detected")
```

### Atomic Operations
For critical files, consider atomic writes:
```python
def atomic_write(self, filename: str, content: str, encoding: str = "utf-8") -> Path:
    """Write file atomically using temporary file."""
    file_path = Path(filename)
    temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
    
    try:
        with temp_path.open(mode="w", encoding=encoding) as f:
            f.write(content)
        temp_path.rename(file_path)  # Atomic on most filesystems
        return file_path
    except Exception as e:
        temp_path.unlink(missing_ok=True)  # Cleanup temp file
        raise APAError(f"Failed to write atomically to {filename}: {str(e)}") from e
```

### Directory Handling
```python
def ensure_directory(self, path: Path) -> Path:
    """Ensure directory exists, creating if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise APAError(f"Failed to create directory {path}: {str(e)}") from e
```

## Testing I/O Operations

### Unit Testing Strategy
- Use temporary directories (`tempfile.TemporaryDirectory`)
- Test both success and failure scenarios
- Mock filesystem operations for error testing
- Verify proper exception translation

### Test Examples
```python
import tempfile
from pathlib import Path

def test_file_writer_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter()
        test_path = Path(temp_dir) / "test.txt"
        
        result = writer.write(str(test_path), "test content")
        
        assert result.exists()
        assert result.read_text() == "test content"

def test_file_writer_permission_error():
    writer = FileWriter()
    
    with pytest.raises(APAError) as exc_info:
        writer.write("/root/forbidden.txt", "content")
    
    assert "Failed to write to file" in str(exc_info.value)
```

## Integration with Application Layer

The FileWriter is used by application services like `ResponseHandler`:

```python
# In response_handler.py
def save_response(self, response: str) -> Path:
    filename = self.generate_filename()
    try:
        return self.file_writer.write(filename, response, encoding="utf-8")
    except Exception as e:
        raise APAError(f"Failed to save response: {str(e)}") from e
```

This pattern keeps file operations abstracted and testable.