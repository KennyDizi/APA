# CLAUDE.md - UI Infrastructure

This file provides guidance for working with user interface components in APA.

## Purpose

This directory contains user interface components that provide visual feedback and interaction. Currently focused on console/terminal UI elements.

## Files Overview

### `console_loading_indicator.py` - Terminal Loading Animation
**Core responsibility**: Provide smooth, visually appealing loading animations for terminal applications.

**Implementation**: Domain interface implementation (`LoadingIndicator`)

**Key Features:**
- Smooth horizontal bar animation with leftward gradient effect
- 50 FPS smooth animation timing
- Thread-safe operation with daemon threads
- Terminal cursor management (hide during animation, restore after)
- Bouncing animation cycle (4 seconds total: 2 seconds forward, 2 seconds backward)
- ANSI color codes for gradient effects

## Loading Indicator Architecture

### Interface Implementation
```python
class ConsoleLoadingIndicator(LoadingIndicator):
    """Implements domain interface for terminal loading animations."""
    
    def start(self) -> None:
        """Start animation in background thread"""
        
    def stop(self) -> None:
        """Stop animation and cleanup"""
```

### Animation System

**Threading Model:**
- Main thread continues processing while animation runs
- Daemon thread for animation (auto-cleanup on program exit)
- Thread-safe start/stop operations

**Timing System:**
```python
frame_interval = 0.02  # 50 FPS target
next_frame_time = time.time()

# Precise timing with drift compensation
sleep_time = next_frame_time - time.time()
if sleep_time > 0:
    time.sleep(sleep_time)
else:
    # Reset timer if behind schedule
    next_frame_time = time.time() + frame_interval
```

**Animation Cycle:**
- 4-second total cycle
- 0-2 seconds: Forward movement (position 0.0 → 9.0)
- 2-4 seconds: Backward movement (position 9.0 → 0.0) 
- Continuous loop while active

### Visual Design

**Gradient Effect:**
```python
# Position-based coloring with direction-dependent gradient
if d < 1:
    # Bright white vs shadow gray based on direction
    color = "\x1b[97m██\x1b[0m" if moving_right else "\x1b[37m██\x1b[0m"
elif d < 2:
    # Reversed colors for gradient effect
    color = "\x1b[37m██\x1b[0m" if moving_right else "\x1b[97m██\x1b[0m"
```

**Terminal Control:**
- Cursor hiding: `\x1b[?25l` (start) → `\x1b[?25h` (stop)
- Line clearing: `\r\x1b[2K` (clear entire line)
- Real-time updates without scrolling

## Development Guidelines

### Adding New UI Components

1. **Implement Domain Interface**: Always implement appropriate domain interface
2. **Thread Safety**: Consider thread safety for interactive components
3. **Resource Cleanup**: Properly cleanup resources (cursors, threads, etc.)
4. **Cross-Platform**: Consider terminal capabilities across platforms

### UI Component Patterns

**Lifecycle Management:**
```python
def start(self):
    if self._running:
        return  # Prevent double-start
    
    self._running = True
    # Initialize resources
    # Start background operations

def stop(self):
    self._running = False
    # Cleanup resources
    # Join threads with timeout
```

**Terminal State Management:**
```python
def __enter__(self):
    self.start()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.stop()
```

### Animation Best Practices

**Smooth Animation:**
- Use consistent frame rates (typically 30-60 FPS)
- Implement proper timing with drift compensation
- Avoid blocking the main thread

**Visual Polish:**
- Use ANSI escape codes for colors and effects
- Clear lines properly to avoid visual artifacts
- Hide cursor during animations, restore after

**Resource Management:**
- Use daemon threads for animations
- Implement proper cleanup in stop methods
- Handle terminal resize events if needed

## ANSI Escape Codes Reference

### Colors
```python
"\x1b[97m"  # Bright white
"\x1b[37m"  # Light gray  
"\x1b[90m"  # Dark gray
"\x1b[0m"   # Reset all formatting
```

### Cursor Control
```python
"\x1b[?25l"  # Hide cursor
"\x1b[?25h"  # Show cursor
"\r\x1b[2K"  # Move to start of line and clear it
```

### Positioning
```python
"\r"         # Move to start of line
"\x1b[2K"    # Clear entire line
"\x1b[A"     # Move cursor up one line
"\x1b[B"     # Move cursor down one line
```

## Testing UI Components

### Unit Testing Strategy
- Mock `sys.stdout` for testing output
- Test start/stop lifecycle
- Verify thread cleanup
- Test animation timing logic

### Example Test Structure
```python
import unittest.mock
from io import StringIO

def test_loading_indicator_output():
    mock_stdout = StringIO()
    
    with unittest.mock.patch('sys.stdout', mock_stdout):
        indicator = ConsoleLoadingIndicator("Testing")
        indicator.start()
        time.sleep(0.1)  # Allow animation frames
        indicator.stop()
    
    output = mock_stdout.getvalue()
    assert "Testing" in output
    assert "\x1b[" in output  # Contains ANSI codes
```

### Integration Testing
- Test with real terminal output
- Verify visual appearance manually
- Test interruption scenarios (Ctrl+C)
- Test rapid start/stop cycles

## Performance Considerations

### CPU Usage
- 50 FPS animation uses minimal CPU (~1-2%)
- Daemon threads auto-cleanup on exit
- Sleep-based timing is CPU-efficient

### Memory Usage
- Minimal memory footprint
- No accumulating buffers or leaks
- Proper thread cleanup prevents memory leaks

### Terminal Responsiveness
- Non-blocking animation (background thread)
- Immediate stop response
- Clean output without artifacts

## Extension Points

### Custom Loading Indicators
```python
class SpinnerLoadingIndicator(LoadingIndicator):
    """Alternative spinner-style indicator"""
    
    def __init__(self):
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        # Implementation...
```

### Progress Indicators
```python
class ProgressIndicator:
    """Progress bar with percentage"""
    
    def update(self, progress: float):
        """Update progress (0.0 to 1.0)"""
        # Implementation...
```

### Interactive Elements
Consider patterns for:
- Input prompts with validation
- Menu selection systems
- Real-time status displays