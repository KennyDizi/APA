from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Prompt:
    """Value object representing a user prompt."""
    content: str
    language: str = "Python"

@dataclass(frozen=True)
class SystemPrompt:
    """Value object representing the system prompt template."""
    template: str
    language: str = "Python"

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        from string import Template
        return Template(self.template).safe_substitute(**kwargs)

@dataclass
class LLMResponse:
    """Value object representing a response from an LLM."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None

@dataclass
class LLMConfig:
    """Value object representing LLM configuration."""
    provider: str
    model: str
    api_key: str
    temperature: Optional[float] = None
    reasoning_effort: Optional[str] = None
    thinking_tokens: Optional[int] = None
    stream: bool = False
    programming_language: str = "Python"
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
