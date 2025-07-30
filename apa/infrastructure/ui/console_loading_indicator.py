import sys
import threading
import time
from typing import Optional
from apa.domain.interfaces import LoadingIndicator

class ConsoleLoadingIndicator(LoadingIndicator):
    """Console-based loading indicator with animation."""

    def __init__(self, message: str = "Processing request", animation_chars: Optional[list] = None):
        self.message = message
        self.animation_chars = animation_chars or ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._running = False
        self._thread = None

    def start(self) -> None:
        """Start the loading animation in a separate thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the loading animation."""
        self._running = False
        if self._thread and self._thread.is_alive():
            # Clear the loading line
            sys.stdout.write("\r" + " " * (len(self.message) + 3) + "\r")
            sys.stdout.flush()
            self._thread.join(timeout=0.1)

    def _animate(self) -> None:
        """Animation loop."""
        i = 0
        while self._running:
            char = self.animation_chars[i % len(self.animation_chars)]
            sys.stdout.write(f"\r{self.message} {char} ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
