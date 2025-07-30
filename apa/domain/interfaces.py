from abc import ABC, abstractmethod

class LoadingIndicator(ABC):
    """Interface for loading indicators in the application."""

    @abstractmethod
    def start(self) -> None:
        """Start the loading animation."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the loading animation."""
        pass
