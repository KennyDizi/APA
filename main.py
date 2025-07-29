import argparse, asyncio, pathlib, sys
import datetime
from apa.config     import load_settings
from apa.infrastructure.llm_client import acompletion

def _generate_filename() -> str:
    """Generate a filename with the format: {day}-{month}-{year}-{hours}-{minute}-{AM or PM}.txt"""
    now = datetime.datetime.now()
    hour = now.hour
    am_pm = "AM" if hour < 12 else "PM"
    
    # Convert to 12-hour format (1-12)
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12  # 0 in 24-hour format is 12 in 12-hour format
    
    return f"{now.day:02d}-{now.month:02d}-{now.year}-{hour_12:02d}-{now.minute:02d}-{am_pm}.txt"

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

    # Collect the full response
    full_response = ""
    if stream:
        # Handle streaming response
        async for chunk in result:
            print(chunk, end='', flush=True)
            full_response += chunk
        print()  # Add newline at the end
    else:
        # Handle non-streaming response
        full_response = result
        print(full_response)

    # Save the response to a file with UTF-8 encoding
    filename = _generate_filename()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_response)
    print(f"Response saved to {filename}")

def main() -> None:
    """Entry point for the APA application.

    Runs the main async function using asyncio.run().
    """
    asyncio.run(_main())

if __name__ == "__main__":
    main()
