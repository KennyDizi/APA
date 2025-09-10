"""Model capability definitions for LLM providers."""

from typing import FrozenSet

# Models that don't support temperature parameter
NO_SUPPORT_TEMPERATURE_MODELS: FrozenSet[str] = frozenset({
    "deepseek/deepseek-reasoner",
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

# Models that support reasoning effort parameter
SUPPORT_REASONING_EFFORT_MODELS: FrozenSet[str] = frozenset({
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

# Models that support developer message role
SUPPORT_DEVELOPER_MESSAGE_MODELS: FrozenSet[str] = frozenset({
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

# Models that support extended thinking tokens
EXTENDED_THINKING_MODELS: FrozenSet[str] = frozenset({
    "anthropic/claude-3-7-sonnet-20250219",
    "claude-3-7-sonnet-20250219",
    "anthropic/claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514",
    "anthropic/claude-opus-4-20250514",
    "claude-opus-4-20250514",
    "claude-opus-4-1-20250805",
    "anthropic/claude-opus-4-1-20250805",
})

# Providers that support the reasoning_effort parameter
REASONING_EFFORT_SUPPORTED_PROVIDERS: FrozenSet[str] = frozenset({"openai"})