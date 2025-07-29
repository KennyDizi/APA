import argparse
import pathlib
import sys
import asyncio
from apa.application.prompt_processor import PromptProcessor
from apa.application.response_handler import ResponseHandler
from apa.domain.models import Prompt, SystemPrompt, LLMConfig
from apa.infrastructure.config.config_loader import ConfigLoader
from apa.infrastructure.llm.llm_client import LLMClient
from apa.infrastructure.io.file_writer import FileWriter

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Async Prompt Application (APA)")
    parser.add_argument(
        "--msg-file",
        required=True,
        type=pathlib.Path,
        help="Path to a .txt file whose contents become the user prompt."
    )
    return parser.parse_args()

def read_prompt_file(path: pathlib.Path) -> str:
    """Read the contents of a prompt file."""
    if not path.exists() or path.suffix.lower() != ".txt":
        sys.exit(f"[ERROR] File '{path}' missing or not a .txt file.")
    return path.read_text(encoding="utf-8")

async def main() -> None:
    """Main application entry point."""
    # Parse command line arguments
    args = parse_args()

    # Load configuration
    config_loader = ConfigLoader(
        config_path=pathlib.Path(__file__).parent / "apa" / "configuration.toml",
        system_prompt_path=pathlib.Path(__file__).parent / "apa" / "system_prompt.toml"
    )

    raw_config = config_loader.load_raw_config()
    resolved_config = config_loader.resolve_provider_config(raw_config)
    system_prompt_content = config_loader.load_system_prompt()

    # Create domain objects
    user_prompt = Prompt(
        content=read_prompt_file(args.msg_file),
        language=raw_config.get("programming_language", "Python")
    )
    system_prompt = SystemPrompt(
        template=system_prompt_content,
        language=raw_config.get("programming_language", "Python")
    )

    # Create LLM configuration
    llm_config = LLMConfig(
        provider=resolved_config["provider"],
        model=raw_config["model"],
        api_key=resolved_config["api_key"],
        temperature=raw_config.get("temperature"),
        reasoning_effort=raw_config.get("reasoning_effort"),
        thinking_tokens=raw_config.get("thinking_tokens"),
        stream=raw_config.get("stream", False),
        programming_language=raw_config.get("programming_language", "Python"),
        fallback_provider=raw_config.get("fallback_provider"),
        fallback_model=raw_config.get("fallback_model")
    )

    # Create infrastructure adapters
    llm_client = LLMClient(llm_config)
    file_writer = FileWriter()

    # Create application services
    prompt_processor = PromptProcessor(llm_client)
    response_handler = ResponseHandler(file_writer)

    # Process the prompt
    if llm_config.stream:
        # Handle streaming response
        full_response = ""
        async for chunk in prompt_processor.process_prompt_stream(
            system_prompt, user_prompt, llm_config
        ):
            print(chunk, end='', flush=True)
            full_response += chunk
        print()  # Add newline at the end
    else:
        # Handle non-streaming response
        full_response = await prompt_processor.process_prompt(
            system_prompt, user_prompt, llm_config
        )
        print(full_response)

    # Save the response
    saved_path = response_handler.save_response(full_response)
    print(f"Response saved to {saved_path}")

def run() -> None:
    """Entry point for the application."""
    asyncio.run(main())

if __name__ == "__main__":
    run()
