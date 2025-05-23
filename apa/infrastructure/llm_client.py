import litellm, asyncio
from typing import Any
from apa.config import load_settings

async def acompletion(system_prompt: str,
                      user_prompt: str,
                      template: str | None = None,
                      model: str | None = None) -> str:
    """Main async completion wrapper requested in the CR."""
    cfg      = load_settings()
    provider = cfg.provider                       # determined in config.py

    # build LiteLLM compatible kwargs
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt.format(template=template or "")},
    ]
    final_model = model or cfg.model or provider
    kwargs: dict[str, Any] = dict(
        model              = final_model,
        messages           = messages,
        temperature        = cfg.temperature,
        api_key            = cfg.api_key,
    )

    # provider specific params ------------------------------
    if provider == "openai" and cfg.reasoning_effort:
        kwargs["reasoning_effort"] = cfg.reasoning_effort

    if provider == "anthropic" and cfg.thinking_tokens:
        kwargs["thinking_tokens"] = cfg.thinking_tokens
    # -------------------------------------------------------

    resp = await litellm.acompletion(**kwargs)     # ✓ async request
    return resp.choices[0].message.content.strip()
