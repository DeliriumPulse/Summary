"""Gemini LLM provider implementation"""
import google.generativeai as genai
from typing import List
from llm.base import LLMProvider, SummaryStyle


class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google API key
            model: Model name to use (default: gemini-2.0-flash-exp)
        """
        super().__init__(api_key)
        self.model_name = model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)
    
    async def summarize(self, messages: List[str], style: SummaryStyle = SummaryStyle.PROFESSIONAL) -> str:
        """
        Summarize messages using Gemini
        
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
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            # Fallback to synchronous if async fails
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error generating summary: {str(e)}"
    
    def validate_api_key(self) -> bool:
        """
        Validate Gemini API key
        
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Try a simple API call to validate
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(model_name=self.model_name)
            response = model.generate_content("test")
            return True
        except Exception:
            return False
