"""Base class for LLM providers"""
from abc import ABC, abstractmethod
from typing import List, Dict
from enum import Enum


class SummaryStyle(str, Enum):
    """Available summary styles"""
    PROFESSIONAL = "Professional"
    FUNNY = "Funny"
    EXECUTIVE = "Executive Summary"
    TECHNICAL = "Technical"
    CASUAL = "Casual"


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str):
        """
        Initialize LLM provider
        
        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key
        self.style_prompts = self._get_style_prompts()
    
    @abstractmethod
    async def summarize(self, messages: List[str], style: SummaryStyle = SummaryStyle.PROFESSIONAL) -> str:
        """
        Summarize a list of messages
        
        Args:
            messages: List of message strings to summarize
            style: Summary style to use
        
        Returns:
            Summary text
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is valid
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _get_style_prompts(self) -> Dict[SummaryStyle, str]:
        """
        Get prompt templates for each summary style
        
        Returns:
            Dictionary mapping styles to prompt templates
        """
        return {
            SummaryStyle.PROFESSIONAL: (
                "You are a professional assistant summarizing a chat conversation. "
                "Provide a clear, concise summary in bullet points. Focus on key topics, "
                "decisions, and action items. Maintain a professional tone. "
                "IMPORTANT: Use HTML formatting for Telegram: <b>text</b> for bold, "
                "<i>text</i> for italic, <code>text</code> for code. Do NOT use Markdown asterisks or underscores."
            ),
            SummaryStyle.FUNNY: (
                "You are a witty assistant summarizing a chat conversation. "
                "Provide a humorous summary in bullet points, using playful language "
                "and emoji where appropriate. Keep it light-hearted but still capture "
                "the main points. 😄 "
                "IMPORTANT: Use HTML formatting for Telegram: <b>text</b> for bold, "
                "<i>text</i> for italic. Do NOT use Markdown asterisks or underscores."
            ),
            SummaryStyle.EXECUTIVE: (
                "You are an executive assistant providing a high-level summary. "
                "Focus ONLY on the most critical points: key decisions, important "
                "announcements, and urgent action items. Keep it extremely brief "
                "(3-5 bullet points max). Use clear, formal language. "
                "IMPORTANT: Use HTML formatting for Telegram: <b>text</b> for bold. "
                "Do NOT use Markdown asterisks."
            ),
            SummaryStyle.TECHNICAL: (
                "You are a technical analyst summarizing a chat conversation. "
                "Focus on technical details, code snippets, system discussions, "
                "and technical decisions. Use precise technical terminology. "
                "Organize by technical topics. "
                "IMPORTANT: Use HTML formatting for Telegram: <b>text</b> for bold, "
                "<code>text</code> for code snippets. Do NOT use Markdown."
            ),
            SummaryStyle.CASUAL: (
                "You are a friendly assistant summarizing a chat conversation. "
                "Keep it casual and conversational, like you're telling a friend "
                "what happened. Use relaxed language and emojis if relevant. "
                "Still capture the main points though! "
                "IMPORTANT: Use HTML formatting for Telegram: <b>text</b> for bold. "
                "Do NOT use Markdown asterisks."
            )
        }
    
    def _format_messages_for_prompt(self, messages: List[str]) -> str:
        """
        Format messages into a prompt string
        
        Args:
            messages: List of message strings
        
        Returns:
            Formatted prompt string
        """
        messages_text = "\n".join(messages)
        return f"""The following is a conversation from a Telegram chat:

{messages_text}

Please summarize the above conversation."""
    
    def _build_prompt(self, messages: List[str], style: SummaryStyle) -> str:
        """
        Build the complete prompt for summarization
        
        Args:
            messages: List of messages to summarize
            style: Summary style to use
        
        Returns:
            Complete prompt string
        """
        style_instruction = self.style_prompts.get(style, self.style_prompts[SummaryStyle.PROFESSIONAL])
        messages_prompt = self._format_messages_for_prompt(messages)
        
        return f"""{style_instruction}

{messages_prompt}"""
