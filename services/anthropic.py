from anthropic import Anthropic
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"

    async def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        with open(self.prompts_dir / prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    async def process_text(self, text: str, style: str) -> str:
        """Process text using specified style."""
        if not text:
            raise ValueError("Input text cannot be empty")
            
        if not style:
            raise ValueError("Style must be specified")
            
        logger.info(f"Processing text with style: {style}")
        logger.debug(f"Input text length: {len(text)}")
        
        try:
            # Load appropriate prompt template
            prompt_file = f"{style}.md"
            prompt_template = await self._load_prompt(prompt_file)
            
            # Format prompt with text
            prompt = prompt_template.format(text=text)
            logger.debug(f"Formatted prompt length: {len(prompt)}")
            
            # Call Anthropic API (synchronously)
            logger.info("Sending request to Anthropic API")
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            if not response or not response.content:
                raise ValueError("Empty response from Anthropic API")
                
            result = response.content[0].text
            logger.info(f"Successfully processed text (output length: {len(result)})")
            return result
            
        except Exception as e:
            logger.error(f"Error processing text with style {style}: {str(e)}")
            raise 