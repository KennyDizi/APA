from typing import Dict, FrozenSet
from apa.domain.exceptions import ConfigurationError

class ConfigValidator:
    """Validates configuration values."""

    ACCEPTED_PROVIDERS: FrozenSet[str] = frozenset({
        "openai", "anthropic", "deepseek", "openrouter"
    })

    PROVIDER_ENV_MAP: Dict[str, str] = {
        "openai":     "OPENAI_API_KEY",
        "anthropic":  "ANTHROPIC_API_KEY",
        "deepseek":   "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }

    def validate_provider(self, provider: str) -> None:
        """Validate that a provider is supported."""
        if provider.lower() not in self.ACCEPTED_PROVIDERS:
            raise ConfigurationError(
                f"Unsupported provider '{provider}'. "
                f"Accepted providers: {', '.join(sorted(self.ACCEPTED_PROVIDERS))}"
            )
