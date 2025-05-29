import litellm, logging, asyncio
from typing import Any, AsyncGenerator
from dataclasses import dataclass
from apa.config import load_settings

# logging setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    # avoid duplicate handlers
    logging.basicConfig(level=logging.INFO)

class CompletionFailureError(Exception):
    """Raised when both primary and fallback providers fail."""
    pass

@dataclass
class ProviderConfig:
    """Encapsulates provider-specific configuration."""
    provider: str
    model: str
    api_key: str

NO_SUPPORT_TEMPERATURE_MODELS = frozenset({
    "deepseek/deepseek-reasoner",
    "openrouter/deepseek/deepseek-r1-0528",
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
})

SUPPORT_REASONING_EFFORT_MODELS = frozenset({
    "o3-mini",
    "o3-mini-2025-01-31",
    "o3",
    "o3-2025-04-16",
    "o4-mini",
    "o4-mini-2025-04-16",
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
})

CLAUDE_EXTENDED_THINKING_MODELS = frozenset({
    "anthropic/claude-3-7-sonnet-20250219",
    "claude-3-7-sonnet-20250219",
    "anthropic/claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514",
    "anthropic/claude-opus-4-20250514",
    "claude-opus-4-20250514",
})

# providers the app currently supports
ACCEPTED_PROVIDERS = frozenset({"openai", "anthropic", "deepseek", "openrouter"})

def _prepare_completion_kwargs(
    provider_config: ProviderConfig,
    messages: list[dict[str, str]],
    cfg: Any,
    stream: bool = False
) -> dict[str, Any]:
    """Prepare kwargs for litellm completion based on model capabilities."""
    model = f"{provider_config.provider}/{provider_config.model}"
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "api_key": provider_config.api_key,
    }

    # Temperature handling
    if provider_config.model in NO_SUPPORT_TEMPERATURE_MODELS:
        logger.info(f"Model '{provider_config.model}' doesn't support temperature")
    else:
        kwargs["temperature"] = cfg.temperature

    # Reasoning effort handling
    if provider_config.model in SUPPORT_REASONING_EFFORT_MODELS and cfg.reasoning_effort:
        logger.info(f"Adding reasoning_effort={cfg.reasoning_effort}")
        kwargs["reasoning_effort"] = cfg.reasoning_effort

    # Claude thinking tokens handling
    if provider_config.model in CLAUDE_EXTENDED_THINKING_MODELS and cfg.thinking_tokens:
        logger.info(f"Adding thinking_tokens={cfg.thinking_tokens}")
        kwargs["thinking"] = {
            "type": "enabled",
            "budget_tokens": cfg.thinking_tokens
        }
        kwargs["temperature"] = 1.0

    if stream:
        kwargs["stream"] = True

    return kwargs

def _prepare_messages(
    system_prompt: str,
    user_prompt: str,
    model: str
) -> list[dict[str, str]]:
    """Prepare messages with appropriate role based on model capabilities."""
    role = "developer" if model in SUPPORT_DEVELOPER_MESSAGE_MODELS else "system"
    logger.info(f"Using role: {role} for model: {model}")
    return [
        {"role": role, "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def _load_provider_config(provider: str, model: str) -> ProviderConfig:
    """Load provider-specific configuration including API key."""
    from apa.config import PROVIDER_ENV_MAP
    import os

    provider_lc = provider.lower()
    if provider_lc not in ACCEPTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{provider}'. "
            f"Accepted providers: {', '.join(sorted(ACCEPTED_PROVIDERS))}"
        )

    # Get API key for the specific provider
    env_var = PROVIDER_ENV_MAP.get(provider_lc)
    if not env_var:
        raise ValueError(f"No environment variable mapping for provider '{provider}'")

    api_key = os.getenv(env_var)
    if not api_key:
        raise EnvironmentError(f"Missing API key for {provider} - set {env_var}")

    return ProviderConfig(provider=provider_lc, model=model, api_key=api_key)

async def _execute_completion(
    provider_config: ProviderConfig,
    messages: list[dict[str, str]],
    cfg: Any,
    stream: bool = False,
    attempt: int = 1,
    is_fallback: bool = False
) -> str | AsyncGenerator[str, None]:
    """Execute a single completion attempt with specific provider configuration."""
    provider_type = "fallback" if is_fallback else "primary"
    model = f"{provider_config.provider}/{provider_config.model}"
    logger.info(
        f"Attempting {provider_type} completion with {model} "
        f"(attempt {attempt})"
    )

    kwargs = _prepare_completion_kwargs(provider_config, messages, cfg, stream)

    try:
        resp = await litellm.acompletion(**kwargs)

        if stream:
            return _stream_response(resp)
        else:
            content = resp.choices[0].message.content.strip()
            if not content:  # Empty response is considered a failure
                raise ValueError("Received empty response from model")
            return content

    except Exception as e:
        logger.error(
            f"{provider_type.capitalize()} provider {provider_config.provider}/{provider_config.model} "
            f"failed on attempt {attempt}: {type(e).__name__}: {e}"
        )
        raise

async def acompletion(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    stream: bool = False,
    settings: Any | None = None
) -> str | AsyncGenerator[str, None]:
    """
    Main async completion wrapper with automatic fallback mechanism.

    Attempts the primary provider/model up to 3 times, then switches to
    the fallback provider/model if configured.

    Args:
        system_prompt: System prompt to guide the model
        user_prompt: User's input prompt
        model: Override model (uses config default if None)
        stream: Whether to stream the response
        settings: Pre-loaded Settings instance (skips duplicate load_settings())

    Returns:
        Completion text or async generator for streaming

    Raises:
        CompletionFailureError: When both primary and fallback providers fail
    """
    cfg = settings or load_settings()

    # Prepare primary provider configuration
    primary_model = model or cfg.model
    primary_config = _load_provider_config(cfg.provider, primary_model)

    # Prepare messages
    messages = _prepare_messages(system_prompt, user_prompt, primary_model)

    # Try primary provider up to 3 times
    for attempt in range(1, 4):
        try:
            return await _execute_completion(
                primary_config, messages, cfg, stream, attempt, is_fallback=False
            )
        except Exception as e:
            if attempt == 3:
                logger.warning(
                    f"Primary provider {primary_config.provider}/{primary_config.model} "
                    f"failed after 3 attempts. Last error: {e}"
                )
                break
            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)

    # Check if fallback is configured
    if not cfg.fallback_provider or not cfg.fallback_model:
        raise CompletionFailureError(
            f"Primary provider {primary_config.provider}/{primary_config.model} failed "
            "and no fallback is configured"
        )

    # Try fallback provider
    logger.info(f"Switching to fallback provider {cfg.fallback_provider}/{cfg.fallback_model}")

    try:
        fallback_config = _load_provider_config(cfg.fallback_provider, cfg.fallback_model)

        # Prepare messages for fallback model
        fallback_messages = _prepare_messages(system_prompt, user_prompt, cfg.fallback_model)

        # Try fallback up to 3 times
        for attempt in range(1, 4):
            try:
                return await _execute_completion(
                    fallback_config, fallback_messages, cfg, stream, attempt, is_fallback=True
                )
            except Exception as e:
                if attempt == 3:
                    raise CompletionFailureError(
                        f"Both primary ({primary_config.provider}/{primary_config.model}) and "
                        f"fallback ({fallback_config.provider}/{fallback_config.model}) providers failed. "
                        f"Last error: {e}"
                    )
                await asyncio.sleep(2 ** attempt)

    except Exception as e:
        if isinstance(e, CompletionFailureError):
            raise
        raise CompletionFailureError(
            f"Failed to initialize fallback provider {cfg.fallback_provider}: {e}"
        )

async def _stream_response(response) -> AsyncGenerator[str, None]:
    """Handle streaming response from LiteLLM."""
    try:
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Error during streaming response: {e}")
        raise
