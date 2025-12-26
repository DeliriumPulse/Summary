"""Main application entry point"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.handlers import BotHandlers
from utils.config_loader import config
from storage.message_store import MessageStore

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Initialize database after bot starts"""
    logger.info("Initializing database...")
    message_store = MessageStore(config.storage_settings.database_path)
    await message_store.initialize()
    logger.info("Database initialized successfully")


async def periodic_cleanup(message_store: MessageStore, interval_hours: int):
    """Periodically clean up old messages"""
    while True:
        await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
        logger.info("Running periodic message cleanup...")
        await message_store.clean_old_messages(config.storage_settings.message_retention_days)


def main():
    """Main application entry point"""
    try:
        # Validate configuration
        config.validate()
        logger.info(f"Starting bot in {config.mode} mode with {config.llm_provider} provider")
        
        # Initialize bot handlers
        handlers = BotHandlers()
        
        # Create application
        application = (
            Application.builder()
            .token(config.telegram_token)
            .post_init(post_init)
            .build()
        )
        
        # Register command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("summary", handlers.summary_command))
        application.add_handler(CommandHandler("settings", handlers.settings_command))
        application.add_handler(CommandHandler("stats", handlers.stats_command))
        
        # Register callback query handler for settings
        application.add_handler(CallbackQueryHandler(handlers.settings_callback))
        
        # Register message handler for logging
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.message_handler)
        )
        
        logger.info("Bot starting... Press Ctrl+C to stop")
        logger.info(f"Messages will be retained for {config.storage_settings.message_retention_days} days")
        
        # Start polling
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file or config.json")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
