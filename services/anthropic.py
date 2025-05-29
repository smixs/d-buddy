from anthropic import Anthropic
import os
from pathlib import Path
import logging
import re
import html

logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
    
    def _sanitize_html(self, text: str) -> str:
        """Sanitize HTML to ensure valid Telegram formatting."""
        if not text:
            return text
            
        # Remove everything before and including <answer> tag if it exists
        answer_match = re.search(r'<answer>\s*', text, re.IGNORECASE)
        if answer_match:
            text = text[answer_match.end():]
        
        # Remove everything after and including </answer> tag if it exists
        end_answer_match = re.search(r'\s*</answer>', text, re.IGNORECASE)
        if end_answer_match:
            text = text[:end_answer_match.start()]
        
        # Remove any [отредактированный текст] or similar placeholders
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove lines starting with common AI annotations
        lines = text.split('\n')
        filtered_lines = []
        for line in lines:
            line_clean = line.strip().lower()
            # Skip lines that are clearly AI annotations/comments
            if (line_clean.startswith('исправлен') or 
                line_clean.startswith('пояснение') or
                line_clean.startswith('комментарий') or
                line_clean.startswith('примечание') or
                'исправленный текст' in line_clean or
                line_clean == 'исправлено:' or
                line_clean == 'пояснение:'):
                continue
            filtered_lines.append(line)
        text = '\n'.join(filtered_lines)
        
        # Allowed Telegram HTML tags
        allowed_tags = ['b', 'i', 'u', 's', 'code', 'pre']
        
        # Track and fix tag balancing using a simple stack approach
        import html.parser
        
        class HTMLBalancer(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack = []
                self.result = ""
                
            def handle_starttag(self, tag, attrs):
                if tag in allowed_tags:
                    self.stack.append(tag)
                    self.result += f'<{tag}>'
                    
            def handle_endtag(self, tag):
                if tag in allowed_tags and tag in self.stack:
                    # Close all tags until we find the matching one
                    while self.stack and self.stack[-1] != tag:
                        closed_tag = self.stack.pop()
                        self.result += f'</{closed_tag}>'
                    if self.stack and self.stack[-1] == tag:
                        self.stack.pop()
                        self.result += f'</{tag}>'
                        
            def handle_data(self, data):
                self.result += data
                
            def close(self):
                # Close any remaining open tags
                while self.stack:
                    tag = self.stack.pop()
                    self.result += f'</{tag}>'
                super().close()
                return self.result
        
        try:
            balancer = HTMLBalancer()
            balancer.feed(text)
            text = balancer.close()
        except:
            # If HTML parsing fails, strip all tags
            text = re.sub(r'<[^>]*>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

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
                model="claude-3-haiku-latest",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            if not response or not response.content:
                raise ValueError("Empty response from Anthropic API")
                
            result = response.content[0].text
            
            # Sanitize HTML to ensure valid Telegram formatting
            sanitized_result = self._sanitize_html(result)
            logger.info(f"Successfully processed text (output length: {len(sanitized_result)})")
            logger.debug(f"HTML sanitization applied: original={len(result)}, sanitized={len(sanitized_result)}")
            
            return sanitized_result
            
        except Exception as e:
            logger.error(f"Error processing text with style {style}: {str(e)}")
            raise 