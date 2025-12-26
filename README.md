# Telegram Chat Summarizer Bot

A production-ready Telegram bot that summarizes chat history using AI (Gemini, OpenAI, or Anthropic). Perfect for enterprise deployment with both hosted and bring-your-own-key (BYOK) modes.

## ✨ Features

- 🤖 **Multi-Provider LLM Support**: Use Gemini, OpenAI, or Anthropic
- 🎨 **Multiple Summary Styles**: Professional, Funny, Executive, Technical, Casual
- 💾 **Automatic Message Logging**: Real-time message storage for future summarization
- 🔒 **Privacy-First**: Configurable message retention period
- 🐳 **Docker Ready**: One-command deployment with Docker Compose
- 🏢 **Enterprise-Ready**: Easy white-labeling and multi-tenant support

## 🚀 Quick Start

### Hosted Mode (Recommended for Single Deployment)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create `.env` file** (copy from `.env.example`):
```bash
cp .env.example .env
```

3. **Configure your environment variables**:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
MODE=hosted
```

4. **Run the bot**:
```bash
python src/main.py
```

### BYOK Mode (Bring-Your-Own-Key)

1. **Create `config/config.json`** (copy from `config/config.example.json`):
```bash
cp config/config.example.json config/config.json
```

2. **Edit `config/config.json`** with your API keys:
```json
{
  "mode": "byok",
  "llm_provider": "openai",
  "api_keys": {
    "openai": "sk-your-key",
    "anthropic": "sk-ant-your-key",
    "gemini": "AIza-your-key"
  },
  "bot": {
    "telegram_token": "your_telegram_bot_token"
  }
}
```

3. **Install and run**:
```bash
pip install -r requirements.txt
python src/main.py
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Create `.env` file** with your configuration
2. **Run**:
```bash
docker-compose up -d
```

### Build and Run Manually

```bash
docker build -t telegram-summarizer .
docker run -d --name summarizer --env-file .env -v $(pwd)/data:/app/data telegram-summarizer
```

## 📖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and introduction |
| `/help` | Detailed help and instructions |
| `/summary [n]` | Summarize last n messages (default: 20) |
| `/settings` | Choose summary style |
| `/stats` | View chat statistics |

## 🎨 Summary Styles

- **👔 Professional**: Clear, formal summaries for business use
- **😄 Funny**: Humorous summaries with emojis
- **📈 Executive**: Ultra-brief, key points only (3-5 bullets)
- **🔧 Technical**: Focus on technical discussions and code
- **💬 Casual**: Friendly, conversational summaries

## ⚙️ Configuration

### Hosted Mode vs BYOK Mode

| Feature | Hosted Mode | BYOK Mode |
|---------|-------------|-----------|
| Configuration | `.env` file | `config.json` file |
| Use Case | Single deployment | Multi-tenant, enterprise |
| API Keys | Environment variables | JSON configuration |
| Hot Reload | Requires restart | Requires restart |

### Environment Variables (Hosted Mode)

```env
# Required
TELEGRAM_BOT_TOKEN=          # Your Telegram bot token
GEMINI_API_KEY=              # Gemini API key (if using Gemini)
LLM_PROVIDER=gemini          # gemini, openai, or anthropic
MODE=hosted                  # hosted or byok

# Optional
DEFAULT_SUMMARY_COUNT=20     # Default number of messages to summarize
MAX_SUMMARY_COUNT=100        # Maximum allowed messages
DEFAULT_STYLE=Professional   # Default summary style
MESSAGE_RETENTION_DAYS=30    # Days to retain messages
CLEANUP_INTERVAL_HOURS=24    # Hours between cleanup runs
DATABASE_PATH=data/messages.db
```

### Config File Structure (BYOK Mode)

See `config/config.example.json` for full structure.

## 🏢 Enterprise White-Labeling Guide

### Customizing the Bot

1. **Bot Name & Avatar**:
   - Change bot name via [@BotFather](https://t.me/botfather)
   - Upload custom avatar via BotFather
   - Update welcome messages in `src/bot/handlers.py`

2. **Multi-Tenant Deployment**:
   - Deploy multiple instances with different tokens
   - Use Docker Compose with multiple services
   - Example:
   ```yaml
   services:
     bot-tenant1:
       image: telegram-summarizer
       env_file: .env.tenant1
     bot-tenant2:
       image: telegram-summarizer
       env_file: .env.tenant2
   ```

3. **API Key Management**:
   - Use separate API keys per tenant
   - Implement key rotation without downtime
   - Monitor usage per tenant

4. **Scaling Considerations**:
   - Use load balancers for high traffic
   - Consider PostgreSQL instead of SQLite for large deployments
   - Implement Redis for distributed user settings

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Project Structure

```
telegram-summarizer/
├── src/
│   ├── bot/           # Bot handlers and commands
│   ├── llm/           # LLM provider implementations
│   ├── storage/       # Database layer
│   ├── utils/         # Utilities (config, text cleaning)
│   └── main.py        # Application entry point
├── config/            # Configuration files
├── tests/             # Test suite
├── data/              # Database storage (created at runtime)
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## 📊 API Rate Limits

| Provider | Model | Rate Limit | Notes |
|----------|-------|------------|-------|
| Gemini | 2.0 Flash | 15 RPM (free tier) | Fast, cost-effective |
| OpenAI | GPT-4o-mini | 200 RPM | Good balance |
| Anthropic | Claude 3.5 Haiku | 50 RPM (tier 1) | High quality |

## 🐛 Troubleshooting

### Bot not responding
- Check that `TELEGRAM_BOT_TOKEN` is correct
- Verify bot has  necessary permissions in group chats
- Check logs: `docker logs summarizer`

### "No messages to summarize"
- Bot only sees messages sent after it was added to the chat
- Telegram Bot API doesn't provide historical messages
- Wait for some messages to accumulate

### Database errors
- Ensure `data/` directory has write permissions
- Check `DATABASE_PATH` configuration
- For Docker: verify volume mount

### LLM API errors
- Verify API key is valid
- Check rate limits for your provider
- Monitor API usage and costs

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review logs for error details

---

Made with ❤️ for better team communication
