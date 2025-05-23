import litellm, logging
from typing import Any
from apa.config import load_settings

# -------------------------------------------------------------------
# logging setup
logger = logging.getLogger(__name__)
if not logger.handlers:                       # avoid duplicate handlers
    logging.basicConfig(level=logging.INFO)
# -------------------------------------------------------------------

NO_SUPPORT_TEMPERATURE_MODELS = [
    "deepseek/deepseek-reasoner",
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
]

SUPPORT_REASONING_EFFORT_MODELS = [
    "o3-mini",
    "o3-mini-2025-01-31",
    "o3",
    "o3-2025-04-16",
    "o4-mini",
    "o4-mini-2025-04-16",
]

SUPPORT_DEVELOPER_MESSAGE_MODELS = [
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
    "gpt-4.1-2025-04-14"
]

CLAUDE_EXTENDED_THINKING_MODELS = [
    "anthropic/claude-3-7-sonnet-20250219",
    "claude-3-7-sonnet-20250219",
    "anthropic/claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514",
    "anthropic/claude-opus-4-20250514",
    "claude-opus-4-20250514",
]

# providers the app currently supports
ACCEPTED_PROVIDERS = {"openai", "anthropic", "deepseek", "openrouter"}

async def acompletion(system_prompt: str,
                      user_prompt: str,
                      model: str | None = None) -> str:
    """Main async completion wrapper."""
    cfg      = load_settings()
    provider = cfg.provider                       # determined in config.py

    # ---------- provider check --------------------------------------
    provider_lc = (provider or "").lower()
    if provider_lc not in ACCEPTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{provider}'. "
            f"Accepted providers: {', '.join(sorted(ACCEPTED_PROVIDERS))}"
        )

    final_model = model or cfg.model

    # ---------- messages -----------------------------------
    sys_role = "developer" if final_model in SUPPORT_DEVELOPER_MESSAGE_MODELS else "system"
    messages = [
        {"role": sys_role, "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    # ---------- kwargs -------------------------------------
    kwargs: dict[str, Any] = {
        "model":    final_model,
        "messages": messages,
        "api_key":  cfg.api_key,
    }

    # -------- temperature ------------------------------------------
    if final_model in NO_SUPPORT_TEMPERATURE_MODELS:
        logger.info(
            "Model '%s' is in NO_SUPPORT_TEMPERATURE_MODELS – skipping temperature.",
            final_model,
        )
    else:
        logger.info(
            "Model '%s' supports temperature – adding temperature=%s.",
            final_model,
            cfg.temperature,
        )
        kwargs["temperature"] = cfg.temperature

    # -------- reasoning_effort -------------------------------------
    if final_model in SUPPORT_REASONING_EFFORT_MODELS:
        logger.info(
            "Model '%s' is in SUPPORT_REASONING_EFFORT_MODELS – adding reasoning_effort=%s.",
            final_model,
            cfg.reasoning_effort,
        )
        if cfg.reasoning_effort:
            kwargs["reasoning_effort"] = cfg.reasoning_effort
    else:
        logger.info(
            "Model '%s' is NOT in SUPPORT_REASONING_EFFORT_MODELS – no reasoning_effort.",
            final_model,
        )

    # -------- thinking_tokens --------------------------------------
    if final_model in CLAUDE_EXTENDED_THINKING_MODELS:
        logger.info(
            "Model '%s' is in CLAUDE_EXTENDED_THINKING_MODELS – adding thinking_tokens=%s.",
            final_model,
            cfg.thinking_tokens,
        )
        if cfg.thinking_tokens:
            kwargs["thinking_tokens"] = cfg.thinking_tokens
    else:
        logger.info(
            "Model '%s' is NOT in CLAUDE_EXTENDED_THINKING_MODELS – no thinking_tokens.",
            final_model,
        )

    resp = await litellm.acompletion(**kwargs)     # ✓ async request
    return resp.choices[0].message.content.strip()
