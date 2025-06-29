import argparse, asyncio, pathlib, sys
from apa.config     import load_settings
from apa.infrastructure.llm_client import acompletion

def _parse_args() -> argparse.Namespace:
    """Parse command line arguments for the APA application.

    Returns:
        argparse.Namespace: Parsed arguments containing msg_file path.

    Raises:
        SystemExit: If required arguments are missing or invalid.
    """
    p = argparse.ArgumentParser(description="Async Prompt Application (APA)")
    p.add_argument("--msg-file", required=True, type=pathlib.Path,
                   help="Path to a .txt file whose contents become the user prompt.")
    return p.parse_args()

def _read_prompt_file(path: pathlib.Path) -> str:
    """Read the contents of a prompt file.

    Args:
        path: Path to the .txt file containing the user prompt.

    Returns:
        str: Contents of the prompt file.

    Raises:
        SystemExit: If file doesn't exist or is not a .txt file.
    """
    if not path.exists() or path.suffix.lower() != ".txt":
        sys.exit(f"[ERROR] File '{path}' missing or not a .txt file.")
    return path.read_text(encoding="utf-8")

async def _main() -> None:
    """Main async function that orchestrates the prompt completion workflow.

    Parses command line arguments, loads configuration, reads the prompt file,
    and calls the completion service. Handles both streaming and non-streaming
    responses appropriately.
    """
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
    """Entry point for the APA application.

    Runs the main async function using asyncio.run().
    """
    asyncio.run(_main())

if __name__ == "__main__":
    main()
