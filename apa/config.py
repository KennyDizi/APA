from __future__ import annotations
import os, tomllib, pathlib, dataclasses as _dc

_cfg_path = pathlib.Path(__file__).with_name("configuration.toml")

_sys_prompt_path = pathlib.Path(__file__).with_name("system_prompt.toml")

# maps provider → expected environment variable
PROVIDER_ENV_MAP: dict[str, str] = {
    "openai":     "OPENAI_API_KEY",
    "anthropic":  "ANTHROPIC_API_KEY",
    "deepseek":   "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

@_dc.dataclass(slots=True)
class Settings:
    system_prompt:  str | None = None          # may come from separate *.toml
    model:          str | None = None
    temperature:    float = 0.2
    reasoning_effort: str | None = "high"
    thinking_tokens:  int | None = 16384

    # resolved at runtime (not in TOML)
    api_key: str | None = None
    provider: str | None = None               # auto-detected from env vars

def load_settings() -> Settings:
    raw = tomllib.loads(_cfg_path.read_text()) if _cfg_path.exists() else {}
    st  = Settings(**raw)

    # ----------------   system prompt  -----------------
    if not (st.system_prompt and str(st.system_prompt).strip()):
        st.system_prompt = _load_system_prompt()   # fall-back to separate file

    # --------- detect provider & API key from environment -------------
    for _prov, _env in PROVIDER_ENV_MAP.items():
        _key = os.getenv(_env)
        if _key:
            st.api_key  = _key
            st.provider = _prov
            break

    if not st.api_key:
        raise EnvironmentError(
            "Missing API key – set one of: " + ", ".join(PROVIDER_ENV_MAP.values())
        )

    return st

# -------------------------------------------------------
def _load_system_prompt() -> str:
    """Read and return the system prompt from apa/system_prompt.toml"""
    if not _sys_prompt_path.exists():
        raise FileNotFoundError(f"System prompt file not found: {_sys_prompt_path}")

    data = tomllib.loads(_sys_prompt_path.read_text())
    prompt = (data.get("system_prompt", "") if isinstance(data, dict) else "").strip()
    if not prompt:
        raise ValueError("`system_prompt` key missing or empty in system_prompt.toml")
    return prompt
