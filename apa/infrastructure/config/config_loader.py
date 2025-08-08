import os
import tomllib
from pathlib import Path
from typing import Dict, Any
from apa.domain.exceptions import ConfigurationError
from apa.infrastructure.config.config_validator import ConfigValidator

class ConfigLoader:
    """Adapter for loading configuration from files and environment."""

    def __init__(self, config_path: Path, system_prompt_path: Path):
        self.config_path = config_path
        self.system_prompt_path = system_prompt_path
        self.validator = ConfigValidator()

    def load_raw_config(self) -> Dict[str, Any]:
        """Load raw configuration from TOML file."""
        if not self.config_path.exists():
            return {}

        try:
            return tomllib.loads(self.config_path.read_text())
        except Exception as e:
            raise ConfigurationError(f"Failed to parse configuration file: {str(e)}") from e

    def load_system_prompt(self) -> str:
        """Load system prompt from TOML file."""
        if not self.system_prompt_path.exists():
            raise ConfigurationError(f"System prompt file not found: {self.system_prompt_path}")

        try:
            data = tomllib.loads(self.system_prompt_path.read_text())
            prompt = data.get("system_prompt", "")
            if not prompt or not isinstance(prompt, str):
                raise ConfigurationError("`system_prompt` key missing or invalid in system_prompt.toml")
            return prompt.strip()
        except Exception as e:
            raise ConfigurationError(f"Failed to load system prompt: {str(e)}") from e

    def resolve_provider_config(self, raw_config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve provider and API key configuration."""
        resolved = raw_config.copy()

        # If provider is specified, validate it
        if 'provider' in resolved and resolved['provider']:
            self.validator.validate_provider(resolved['provider'])

        # Auto-detect provider if not specified
        if not resolved.get('provider'):
            for provider, env_var in self.validator.PROVIDER_ENV_MAP.items():
                if os.getenv(env_var):
                    resolved['provider'] = provider
                    resolved['api_key'] = os.getenv(env_var)
                    break

        # If provider is specified but no API key found
        if resolved.get('provider') and not resolved.get('api_key'):
            env_var = self.validator.PROVIDER_ENV_MAP.get(resolved['provider'].lower())
            if env_var:
                api_key = os.getenv(env_var)
                if api_key:
                    resolved['api_key'] = api_key
                else:
                    raise ConfigurationError(
                        f"Missing {env_var} for provider '{resolved['provider']}'"
                    )
            else:
                raise ConfigurationError(
                    f"Unsupported provider '{resolved['provider']}' in configuration"
                )

        # If no provider/api key found at all
        if not resolved.get('provider') or not resolved.get('api_key'):
            raise ConfigurationError(
                "Missing API key – set one of: " +
                ", ".join(self.validator.PROVIDER_ENV_MAP.values())
            )

        return resolved
