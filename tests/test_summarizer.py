"""Unit tests for core summarization functionality"""
import pytest
from datetime import datetime
from src.utils.text_cleaner import TextCleaner
from tests.mock_data import generate_mock_messages, generate_mock_media_messages


class TestTextCleaner:
    """Test text cleaning functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.cleaner = TextCleaner(remove_urls=True, remove_commands=True)
    
    def test_remove_urls(self):
        """Test URL removal"""
        text = "Check this out https://example.com/page and www.another.com"
        cleaned = self.cleaner.clean_message(text)
        assert "https://example.com" not in cleaned
        assert "www.another.com" not in cleaned
    
    def test_remove_commands(self):
        """Test command removal"""
        text = "/start hello everyone"
        cleaned = self.cleaner.clean_message(text)
        assert "/start" not in cleaned
        assert "hello everyone" in cleaned
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        text = "Hello    world   with   spaces"
        cleaned = self.cleaner.clean_message(text)
        assert "  " not in cleaned
        assert cleaned == "Hello world with spaces"
    
    def test_handle_media_messages(self):
        """Test media message handling"""
        messages = generate_mock_media_messages()
        cleaned = self.cleaner.clean_messages(messages)
        
        # Should have descriptive text for media
        assert any("[Photo]" in msg for msg in cleaned)
        assert any("[Video]" in msg for msg in cleaned)
    
    def test_clean_messages_list(self):
        """Test cleaning a list of messages"""
        messages = generate_mock_messages(10)
        cleaned = self.cleaner.clean_messages(messages)
        
        # Should return non-empty list
        assert len(cleaned) > 0
        
        # Each message should have username prefix
        for msg in cleaned:
            assert ":" in msg


class TestMessageFormatting:
    """Test message formatting for LLM prompts"""
    
    def test_message_count(self):
        """Test that correct number of messages are processed"""
        messages = generate_mock_messages(20)
        cleaner = TextCleaner()
        cleaned = cleaner.clean_messages(messages)
        
        # Should preserve all non-system messages
        assert len(cleaned) > 0
        assert len(cleaned) <= 20
    
    def test_empty_messages(self):
        """Test handling of empty message list"""
        cleaner = TextCleaner()
        cleaned = cleaner.clean_messages([])
        assert cleaned == []


@pytest.mark.asyncio
class TestSummarizationIntegration:
    """Integration tests for summarization (requires API keys)"""
    
    async def test_mock_summarization(self):
        """Test summarization with mock data"""
        from tests.mock_data import PROFESSIONAL_CONVERSATION
        
        # This is a placeholder test - actual LLM testing requires API keys
        messages = PROFESSIONAL_CONVERSATION
        assert len(messages) > 0
        assert all(":" in msg for msg in messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
