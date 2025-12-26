"""Tests for LLM provider implementations"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.llm.base import SummaryStyle, LLMProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.anthropic_provider import AnthropicProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing base class"""
    
    async def summarize(self, messages, style=SummaryStyle.PROFESSIONAL):
        return "Mock summary"
    
    def validate_api_key(self):
        return len(self.api_key) > 0


class TestLLMProviderBase:
    """Test base LLM provider functionality"""
    
    def test_style_prompts(self):
        """Test that all style prompts are defined"""
        provider = MockLLMProvider("test-key")
        
        for style in SummaryStyle:
            assert style in provider.style_prompts
            assert len(provider.style_prompts[style]) > 0
    
    def test_format_messages(self):
        """Test message formatting for prompts"""
        provider = MockLLMProvider("test-key")
        messages = ["alice: Hello", "bob: Hi there"]
        
        formatted = provider._format_messages_for_prompt(messages)
        assert "alice: Hello" in formatted
        assert "bob: Hi there" in formatted
    
    def test_build_prompt(self):
        """Test complete prompt building"""
        provider = MockLLMProvider("test-key")
        messages = ["alice: Hello", "bob: Hi"]
        
        prompt = provider._build_prompt(messages, SummaryStyle.FUNNY)
        assert "alice: Hello" in prompt
        assert "bob: Hi" in prompt
        # Should include style instruction
        assert len(prompt) > len("\n".join(messages))


@pytest.mark.asyncio
class TestGeminiProvider:
    """Test Gemini provider (with mocks)"""
    
    async def test_summarize_with_mock(self):
        """Test summarization with mocked API"""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            # Setup mock
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "This is a mock summary"
            mock_model.generate_content = MagicMock(return_value=mock_response)
            mock_model_class.return_value = mock_model
            
            provider = GeminiProvider("test-api-key")
            provider.model = mock_model
            
            messages = ["alice: Hello", "bob: Hi"]
            summary = await provider.summarize(messages)
            
            # Should call the model
            mock_model.generate_content.assert_called_once()
            assert summary == "This is a mock summary"
    
    def test_api_key_validation(self):
        """Test API key validation"""
        provider = GeminiProvider("test-key")
        # With mock, validation would need actual API access
        # This is a placeholder
        assert provider.api_key == "test-key"


@pytest.mark.asyncio
class TestOpenAIProvider:
    """Test OpenAI provider (with mocks)"""
    
    async def test_summarize_with_mock(self):
        """Test summarization with mocked API"""
        with patch('openai.AsyncOpenAI') as mock_client_class:
            # Setup mock
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Mock OpenAI summary"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            provider = OpenAIProvider("test-api-key")
            provider.client = mock_client
            
            messages = ["alice: Hello", "bob: Hi"]
            summary = await provider.summarize(messages)
            
            # Should call the API
            mock_client.chat.completions.create.assert_called_once()
            assert summary == "Mock OpenAI summary"


@pytest.mark.asyncio
class TestAnthropicProvider:
    """Test Anthropic provider (with mocks)"""
    
    async def test_summarize_with_mock(self):
        """Test summarization with mocked API"""
        with patch('anthropic.AsyncAnthropic') as mock_client_class:
            # Setup mock
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_content = MagicMock()
            mock_content.text = "Mock Anthropic summary"
            mock_response.content = [mock_content]
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            provider = AnthropicProvider("test-api-key")
            provider.client = mock_client
            
            messages = ["alice: Hello", "bob: Hi"]
            summary = await provider.summarize(messages)
            
            # Should call the API
            mock_client.messages.create.assert_called_once()
            assert summary == "Mock Anthropic summary"


@pytest.mark.asyncio
class TestSummaryStyles:
    """Test different summary styles"""
    
    async def test_all_styles_work(self):
        """Test that all summary styles can be used"""
        provider = MockLLMProvider("test-key")
        messages = ["alice: Hello", "bob: Hi"]
        
        for style in SummaryStyle:
            summary = await provider.summarize(messages, style)
            assert summary is not None
            assert len(summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
