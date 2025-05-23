import litellm, asyncio
from typing import Any
from apa.config import load_settings

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

async def acompletion(system_prompt: str,
                      user_prompt: str,
                      model: str | None = None) -> str:
    """Main async completion wrapper."""
    cfg      = load_settings()
    provider = cfg.provider                       # determined in config.py

    final_model = model or cfg.model or provider

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

    if final_model not in NO_SUPPORT_TEMPERATURE_MODELS:
        kwargs["temperature"] = cfg.temperature

    if final_model in SUPPORT_REASONING_EFFORT_MODELS and cfg.reasoning_effort:
        kwargs["reasoning_effort"] = cfg.reasoning_effort

    if final_model in CLAUDE_EXTENDED_THINKING_MODELS and cfg.thinking_tokens:
        kwargs["thinking_tokens"]  = cfg.thinking_tokens

    resp = await litellm.acompletion(**kwargs)     # ✓ async request
    return resp.choices[0].message.content.strip()
