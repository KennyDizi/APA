import litellm
from typing import Dict, Any, AsyncGenerator, Optional
from apa.domain.models import LLMConfig
from apa.domain.exceptions import ProviderError

class LLMClient:
    """Adapter for interacting with LLM providers through LiteLLM."""

    NO_SUPPORT_TEMPERATURE_MODELS = frozenset({
        "deepseek/deepseek-reasoner",
        "deepseek/deepseek-r1-0528",
        "qwen/qwen3-235b-a22b-thinking-2507",
        "o1-mini",
        "o1-mini-2024-09-12",
        "o1",
        "o1-2024-12-17",
        "o3-mini",
        "o3-mini-2025-01-31",
        "o1-preview",
        "o3",
        "o3-2025-04-16",
        "o4-mini",
        "o4-mini-2025-04-16",
        "gpt-5-2025-08-07",
        "gpt-5",
    })

    SUPPORT_REASONING_EFFORT_MODELS = frozenset({
        "o3-mini",
        "o3-mini-2025-01-31",
        "o3",
        "o3-2025-04-16",
        "o4-mini",
        "o4-mini-2025-04-16",
        "qwen/qwen3-235b-a22b-thinking-2507",
        "gpt-5-2025-08-07",
        "gpt-5",
    })

    SUPPORT_DEVELOPER_MESSAGE_MODELS = frozenset({
        "o1",
        "o1-2024-12-17",
        "o3-mini",
        "o3-mini-2025-01-31",
        "o1-pro",
        "o1-pro-2025-03-19",
        "o3",
        "o3-2025-04-16",
        "o4-mini",
        "o4-mini-2025-04-16",
        "gpt-4.1",
        "gpt-4.1-2025-04-14",
        "gpt-5-2025-08-07",
        "gpt-5",
    })

    EXTENDED_THINKING_MODELS = frozenset({
        "anthropic/claude-3-7-sonnet-20250219",
        "claude-3-7-sonnet-20250219",
        "anthropic/claude-sonnet-4-20250514",
        "claude-sonnet-4-20250514",
        "anthropic/claude-opus-4-20250514",
        "claude-opus-4-20250514",
        "gemini/gemini-2.5-pro",
        "google/gemini-2.5-pro",
        "claude-opus-4-1-20250805",
        "anthropic/claude-opus-4-1-20250805",
    })

    # Providers that support the reasoning_effort parameter
    REASONING_EFFORT_SUPPORTED_PROVIDERS = frozenset({"openai"})

    def __init__(self, config: LLMConfig):
        self.config = config

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        stream: bool = False,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a completion from the LLM."""
        try:
            # Prepare messages
            messages = self._prepare_messages(system_prompt, user_prompt, model or self.config.model)

            # Prepare kwargs for LiteLLM
            kwargs = self._prepare_completion_kwargs(
                messages,
                model or self.config.model,
                temperature or self.config.temperature,
                stream
            )

            # Call LiteLLM
            response = await litellm.acompletion(**kwargs)

            # Extract content
            content = response.choices[0].message.content.strip()
            if not content:
                raise ProviderError("Received empty response from model")

            return content

        except Exception as e:
            raise ProviderError(f"LLM provider failed: {str(e)}") from e

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming completion from the LLM."""
        try:
            # Prepare messages
            messages = self._prepare_messages(system_prompt, user_prompt, model or self.config.model)

            # Prepare kwargs for LiteLLM
            kwargs = self._prepare_completion_kwargs(
                messages,
                model or self.config.model,
                temperature or self.config.temperature,
                True  # Force stream=True
            )

            # Call LiteLLM with streaming
            response = await litellm.acompletion(**kwargs)

            # Stream the response
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise ProviderError(f"LLM provider failed during streaming: {str(e)}") from e

    def _prepare_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str
    ) -> list[dict[str, str]]:
        """Prepare messages with appropriate role based on model capabilities."""
        role = "developer" if model in self.SUPPORT_DEVELOPER_MESSAGE_MODELS else "system"
        return [
            {"role": role, "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _prepare_completion_kwargs(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: Optional[float],
        stream: bool
    ) -> dict[str, Any]:
        """Prepare kwargs for litellm completion based on model capabilities."""

        kwargs: dict[str, Any] = {
            "model": f"{self.config.provider}/{model}",
            "messages": messages,
            "api_key": self.config.api_key,
        }

        # Temperature handling
        if model not in self.NO_SUPPORT_TEMPERATURE_MODELS and temperature is not None:
            print(f"Setting temperature to {temperature}")
            kwargs["temperature"] = temperature

        # Reasoning effort handling - only add if provider supports it
        if (model in self.SUPPORT_REASONING_EFFORT_MODELS and
            self.config.provider in self.REASONING_EFFORT_SUPPORTED_PROVIDERS and
            self.config.reasoning_effort):
            print(f"Setting reasoning effort to {self.config.reasoning_effort}")
            kwargs["reasoning_effort"] = self.config.reasoning_effort

        # Thinking tokens handling
        if (model in self.EXTENDED_THINKING_MODELS or f'{self.config.provider}/{model}' in self.EXTENDED_THINKING_MODELS) and self.config.thinking_tokens:
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.config.thinking_tokens
            }
            kwargs["temperature"] = 1.0

        if stream:
            kwargs["stream"] = True

        return kwargs
