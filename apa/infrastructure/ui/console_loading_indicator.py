import sys
import threading
import time
from typing import Optional
from apa.domain.interfaces import LoadingIndicator

class ConsoleLoadingIndicator(LoadingIndicator):
    """Console-based loading indicator with horizontal bar animation featuring leftward gradient."""

    def __init__(self, message: str = "Processing request"):
        self.message = message
        self._running = False
        self._thread = None
        self._start_time = 0.0

    def start(self) -> None:
        """Start the loading animation in a separate thread."""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()

        # Hide terminal cursor
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the loading animation and clear the line."""
        self._running = False
        if self._thread and self._thread.is_alive():
            # Clear the entire line
            sys.stdout.write("\r\x1b[2K")
            sys.stdout.flush()
            self._thread.join(timeout=0.1)

        # Show terminal cursor
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    def _render_frame(self, head_pos: float) -> str:
        """Generate frame string based on head position (0.0-9.0)."""
        frame = []
        for i in range(10):
            d = head_pos - i
            if d < 0 or d > 2:
                frame.append("  ")  # Invisible
            elif d < 1:
                frame.append("\x1b[97m██\x1b[0m")  # Bright white
            elif d < 2:
                frame.append("\x1b[37m██\x1b[0m")  # Light gray
            else:
                frame.append("\x1b[90m██\x1b[0m")  # Dark gray
        return ''.join(frame)

    def _animate(self) -> None:
        """Animation loop with precise timing for the horizontal bar."""
        frame_interval = 0.02  # 50 FPS (1/50 = 0.02)
        next_frame_time = time.time()

        # Print initial prompt without newline
        sys.stdout.write(f"\r{self.message} ")
        sys.stdout.flush()

        while self._running:
            # Calculate elapsed time within the 4-second cycle
            elapsed = time.time() - self._start_time
            cycle_time = elapsed % 4.0

            # Calculate head position (0.0-9.0)
            if cycle_time < 2.0:
                # Forward movement: 0.0 → 9.0 in 2 seconds
                head_pos = (cycle_time / 2.0) * 9.0
            else:
                # Backward movement: 9.0 → 0.0 in 2 seconds
                head_pos = 9.0 - ((cycle_time - 2.0) / 2.0) * 9.0

            # Render and display frame
            frame = self._render_frame(head_pos)
            sys.stdout.write(f"\r\x1b[2K{self.message} {frame}")
            sys.stdout.flush()

            # Calculate next frame time for consistent 50 FPS
            next_frame_time += frame_interval
            sleep_time = next_frame_time - time.time()

            # Handle potential drift
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If we're behind schedule, reset the timer to avoid compounding errors
                next_frame_time = time.time() + frame_interval
