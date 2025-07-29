from typing import AsyncGenerator
from apa.domain.models import Prompt, SystemPrompt, LLMConfig
from apa.domain.exceptions import PromptProcessingError

class PromptProcessor:
    """Application service for processing prompts through LLMs."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def process_prompt(
        self,
        system_prompt: SystemPrompt,
        user_prompt: Prompt,
        llm_config: LLMConfig
    ) -> str:
        """Process a user prompt with the given system prompt and LLM configuration."""
        try:
            # Render the system prompt with language information
            rendered_system_prompt = system_prompt.render(
                programming_language=user_prompt.language
            )

            # Process through LLM
            return await self.llm_client.generate_completion(
                system_prompt=rendered_system_prompt,
                user_prompt=user_prompt.content,
                model=llm_config.model,
                stream=llm_config.stream,
                temperature=llm_config.temperature
            )
        except Exception as e:
            raise PromptProcessingError(f"Failed to process prompt: {str(e)}") from e

    async def process_prompt_stream(
        self,
        system_prompt: SystemPrompt,
        user_prompt: Prompt,
        llm_config: LLMConfig
    ) -> AsyncGenerator[str, None]:
        """Process a user prompt with streaming response."""
        try:
            # Render the system prompt with language information
            rendered_system_prompt = system_prompt.render(
                programming_language=user_prompt.language
            )

            # Process through LLM with streaming
            async for chunk in self.llm_client.generate_completion_stream(
                system_prompt=rendered_system_prompt,
                user_prompt=user_prompt.content,
                model=llm_config.model,
                temperature=llm_config.temperature
            ):
                yield chunk
        except Exception as e:
            raise PromptProcessingError(f"Failed to process prompt with streaming: {str(e)}") from e
