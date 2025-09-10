import litellm
from typing import Any, AsyncGenerator, Optional
from apa.domain.models import LLMConfig
from apa.domain.exceptions import ProviderError
from .model_capabilities import (
    NO_SUPPORT_TEMPERATURE_MODELS,
    SUPPORT_REASONING_EFFORT_MODELS,
    SUPPORT_DEVELOPER_MESSAGE_MODELS,
    EXTENDED_THINKING_MODELS,
    REASONING_EFFORT_SUPPORTED_PROVIDERS,
)

class LLMClient:
    """Adapter for interacting with LLM providers through LiteLLM."""

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
        role = "developer" if model in SUPPORT_DEVELOPER_MESSAGE_MODELS else "system"
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

        self._add_temperature_config(kwargs, model, temperature)
        self._add_reasoning_effort_config(kwargs, model)
        self._add_thinking_tokens_config(kwargs, model)

        if stream:
            kwargs["stream"] = True

        return kwargs

    def _add_temperature_config(
        self,
        kwargs: dict[str, Any],
        model: str,
        temperature: Optional[float]
    ) -> None:
        """Add temperature configuration if supported by model."""
        if model not in NO_SUPPORT_TEMPERATURE_MODELS and temperature is not None:
            kwargs["temperature"] = temperature

    def _add_reasoning_effort_config(self, kwargs: dict[str, Any], model: str) -> None:
        """Add reasoning effort configuration if supported."""
        if (model in SUPPORT_REASONING_EFFORT_MODELS and
            self.config.provider in REASONING_EFFORT_SUPPORTED_PROVIDERS and
            self.config.reasoning_effort):
            kwargs["reasoning_effort"] = self.config.reasoning_effort
            kwargs["allowed_openai_params"] = ["reasoning_effort"]

    def _add_thinking_tokens_config(self, kwargs: dict[str, Any], model: str) -> None:
        """Add thinking tokens configuration if supported."""
        full_model_name = f'{self.config.provider}/{model}'
        if ((model in EXTENDED_THINKING_MODELS or full_model_name in EXTENDED_THINKING_MODELS) 
            and self.config.thinking_tokens):
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.config.thinking_tokens
            }
            kwargs["temperature"] = 1.0
