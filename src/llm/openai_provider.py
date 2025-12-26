"""OpenAI LLM provider implementation"""
from openai import AsyncOpenAI
from typing import List
from llm.base import LLMProvider, SummaryStyle


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model name to use (default: gpt-4o-mini)
        """
        super().__init__(api_key)
        self.model_name = model
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def summarize(self, messages: List[str], style: SummaryStyle = SummaryStyle.PROFESSIONAL) -> str:
        """
        Summarize messages using OpenAI
        
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
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes chat conversations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key
        
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            # Try to list models to validate key
            client.models.list()
            return True
        except Exception:
            return False
