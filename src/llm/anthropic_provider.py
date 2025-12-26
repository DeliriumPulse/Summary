"""Anthropic LLM provider implementation"""
from anthropic import AsyncAnthropic
from typing import List
from llm.base import LLMProvider, SummaryStyle


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            model: Model name to use (default: claude-3-5-haiku-20241022)
        """
        super().__init__(api_key)
        self.model_name = model
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def summarize(self, messages: List[str], style: SummaryStyle = SummaryStyle.PROFESSIONAL) -> str:
        """
        Summarize messages using Anthropic Claude
        
        Args:
            messages: List of message strings to summarize
            style: Summary style to use
        
        Returns:
            Summary text
        """
        if not messages:
            return "No messages to summarize."
        
        prompt = self._build_prompt(messages, style)
        
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def validate_api_key(self) -> bool:
        """
        Validate Anthropic API key
        
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            # Try a minimal API call to validate
            client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
