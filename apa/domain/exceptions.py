class APAError(Exception):
    """Base exception for APA application."""
    pass

class ConfigurationError(APAError):
    """Raised when configuration is invalid."""
    pass

class ProviderError(APAError):
    """Raised when there's an issue with an LLM provider."""
    pass

class PromptProcessingError(APAError):
    """Raised when prompt processing fails."""
    pass
