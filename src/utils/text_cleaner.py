"""Text cleaning utilities for message preprocessing"""
import re
from typing import List, Dict, Any


class TextCleaner:
    """Clean and preprocess Telegram messages for summarization"""
    
    def __init__(self, remove_urls: bool = True, remove_commands: bool = True):
        """
        Initialize text cleaner
        
        Args:
            remove_urls: Whether to remove URLs from messages
            remove_commands: Whether to remove bot commands
        """
        self.remove_urls = remove_urls
        self.remove_commands = remove_commands
    
    def clean_message(self, text: str, message_data: Dict[str, Any] = None) -> str:
        """
        Clean a single message
        
        Args:
            text: Message text to clean
            message_data: Optional message metadata
        
        Returns:
            Cleaned message text
        """
        if not text or not text.strip():
            return ""
        
        # Remove URLs if configured
        if self.remove_urls:
            text = self._remove_urls(text)
        
        # Remove bot commands if configured
        if self.remove_commands:
            text = self._remove_commands(text)
        
        # Normalize whitespace
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def clean_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Clean a list of messages
        
        Args:
            messages: List of message dictionaries with 'text' and optional metadata
        
        Returns:
            List of cleaned message strings
        """
        cleaned = []
        
        for msg in messages:
            # Skip system messages
            if self._is_system_message(msg):
                continue
            
            # Handle media messages
            text = self._handle_media_message(msg)
            
            # Clean the text
            cleaned_text = self.clean_message(text, msg)
            
            if cleaned_text:
                # Add username prefix if available
                username = msg.get('username', 'Unknown')
                cleaned.append(f"{username}: {cleaned_text}")
        
        return cleaned
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        # Match http/https URLs
        text = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            '',
            text
        )
        # Match www URLs
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+])+', '', text)
        return text
    
    def _remove_commands(self, text: str) -> str:
        """Remove bot commands from text"""
        # Remove commands like /start, /summary, etc.
        text = re.sub(r'^/\w+\s*', '', text)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _is_system_message(self, message: Dict[str, Any]) -> bool:
        """Check if a message is a system message"""
        # Check for common system message indicators
        text = message.get('text', '')
        
        # Common system message patterns
        system_patterns = [
            r'^.+ joined the group$',
            r'^.+ left the group$',
            r'^.+ was added$',
            r'^.+ was removed$',
            r'^Group photo updated$',
            r'^Group name changed to',
        ]
        
        for pattern in system_patterns:
            if re.match(pattern, text):
                return True
        
        # Check if message has system message type
        if message.get('is_system_message', False):
            return True
        
        return False
    
    def _handle_media_message(self, message: Dict[str, Any]) -> str:
        """Handle media messages by replacing with descriptive text"""
        text = message.get('text', '')
        
        # If there's text, return it
        if text:
            return text
        
        # Otherwise, check for media types
        if message.get('photo'):
            caption = message.get('caption', '')
            return f"[Photo]{' - ' + caption if caption else ''}"
        elif message.get('video'):
            caption = message.get('caption', '')
            return f"[Video]{' - ' + caption if caption else ''}"
        elif message.get('document'):
            filename = message.get('document', {}).get('file_name', 'file')
            return f"[Document: {filename}]"
        elif message.get('sticker'):
            emoji = message.get('sticker', {}).get('emoji', '')
            return f"[Sticker{': ' + emoji if emoji else ''}]"
        elif message.get('voice'):
            return "[Voice message]"
        elif message.get('audio'):
            return "[Audio]"
        elif message.get('location'):
            return "[Location]"
        elif message.get('poll'):
            question = message.get('poll', {}).get('question', '')
            return f"[Poll: {question}]"
        
        # If no recognized media type, return empty string
        return ""
