from typing import AsyncGenerator, Optional
from apa.domain.models import Prompt, SystemPrompt, LLMConfig
from apa.domain.exceptions import PromptProcessingError
from apa.domain.interfaces import LoadingIndicator

class PromptProcessor:
    """Application service for processing prompts through LLMs."""

    def __init__(self, llm_client, loading_indicator: Optional[LoadingIndicator] = None):
        self.llm_client = llm_client
        self.loading_indicator = loading_indicator

    async def process_prompt(
        self,
        system_prompt: SystemPrompt,
        user_prompt: Prompt,
        llm_config: LLMConfig
    ) -> str:
        """Process a user prompt with the given system prompt and LLM configuration."""
        try:
            if self.loading_indicator and not llm_config.stream:
                self.loading_indicator.start()

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
        finally:
            if self.loading_indicator and not llm_config.stream:
                self.loading_indicator.stop()

    async def process_prompt_stream(
        self,
        system_prompt: SystemPrompt,
        user_prompt: Prompt,
        llm_config: LLMConfig
    ) -> AsyncGenerator[str, None]:
        """Process a user prompt with streaming response."""
        try:
            if self.loading_indicator:
                self.loading_indicator.start()

            # Render the system prompt with language information
            rendered_system_prompt = system_prompt.render(
                programming_language=user_prompt.language
            )

            # Process through LLM with streaming
            stream = self.llm_client.generate_completion_stream(
                system_prompt=rendered_system_prompt,
                user_prompt=user_prompt.content,
                model=llm_config.model,
                temperature=llm_config.temperature
            )

            # Handle first chunk (where we wait for initial response)
            try:
                first_chunk = await stream.__anext__()
                if self.loading_indicator:
                    self.loading_indicator.stop()
                yield first_chunk
            except StopAsyncIteration:
                # Stream was empty - stop loading indicator and raise specific error
                if self.loading_indicator:
                    self.loading_indicator.stop()
                raise PromptProcessingError("Received empty response from LLM") from None

            # Yield remaining chunks
            async for chunk in stream:
                yield chunk

        except Exception as e:
            if self.loading_indicator:
                self.loading_indicator.stop()
            raise PromptProcessingError(f"Failed to process prompt with streaming: {str(e)}") from e
