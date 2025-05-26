import argparse, asyncio, pathlib, sys
from apa.services import acompletion
from apa.config     import load_settings

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Async Prompt Application (APA)")
    p.add_argument("--msg-file", required=True, type=pathlib.Path,
                   help="Path to a .txt file whose contents become the user prompt.")
    return p.parse_args()

def _read_prompt_file(path: pathlib.Path) -> str:
    if not path.exists() or path.suffix.lower() != ".txt":
        sys.exit(f"[ERROR] File '{path}' missing or not a .txt file.")
    return path.read_text(encoding="utf-8")

async def _main() -> None:
    args         = _parse_args()
    user_prompt  = _read_prompt_file(args.msg_file)
    cfg          = load_settings()
    sys_prompt   = cfg.system_prompt
    stream       = cfg.stream

    result = await acompletion(sys_prompt, user_prompt, model=cfg.model, stream=stream, settings=cfg)

    if stream:
        # Handle streaming response
        async for chunk in result:
            print(chunk, end='', flush=True)
        print()  # Add newline at the end
    else:
        # Handle non-streaming response
        print(result)

def main() -> None:
    asyncio.run(_main())

if __name__ == "__main__":
    main()
