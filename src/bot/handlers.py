"""Bot command handlers"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import List, Dict, Any
from datetime import datetime

from llm.base import SummaryStyle
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider
from llm.anthropic_provider import AnthropicProvider
from storage.message_store import MessageStore
from utils.text_cleaner import TextCleaner
from utils.config_loader import config

logger = logging.getLogger(__name__)


class BotHandlers:
    """Telegram bot command handlers"""
    
    def __init__(self):
        """Initialize bot handlers"""
        self.message_store = MessageStore(config.storage_settings.database_path)
        self.text_cleaner = TextCleaner()
        self.llm_provider = self._initialize_llm_provider()
    
    def _initialize_llm_provider(self):
        """Initialize the appropriate LLM provider based on config"""
        provider = config.llm_provider
        api_key = config.get_api_key(provider)
        
        if not api_key:
            raise ValueError(f"No API key found for provider: {provider}")
        
        if provider == "gemini":
            return GeminiProvider(api_key)
        elif provider == "openai":
            return OpenAIProvider(api_key)
        elif provider == "anthropic":
            return AnthropicProvider(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "👋 Welcome to <b>Chat Summarizer Bot</b>!\n\n"
            "I can summarize your chat history in different styles.\n\n"
            "<b>Commands:</b>\n"
            "• /summary [n] - Summarize last n messages (default: 20)\n"
            "• /settings - Change summary style\n"
            "• /stats - View chat statistics\n"
            "• /help - Show this help message\n\n"
            "I'll automatically save messages for future summarization. "
            "Just add me to a group and use /summary when you need a quick recap!"
        )
        await update.message.reply_text(welcome_message, parse_mode='HTML')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "<b>Chat Summarizer Bot - Help</b>\n\n"
            "<b>Commands:</b>\n"
            "• /summary - Summarize last 20 messages\n"
            "• /summary 50 - Summarize last 50 messages\n"
            "• /settings - Choose summary style:\n"
            "  - Professional: Clear and formal\n"
            "  - Funny: Humorous with emojis\n"
            "  - Executive: Brief, key points only\n"
            "  - Technical: Focus on technical details\n"
            "  - Casual: Friendly and conversational\n"
            "• /stats - View chat statistics\n\n"
            "<b>How it works:</b>\n"
            "I automatically save messages from your chats. When you use /summary, "
            "I analyze recent messages and create a concise summary based on your "
            "selected style.\n\n"
            "<b>Privacy:</b>\n"
            f"Messages are stored for {config.storage_settings.message_retention_days} days, "
            "then automatically deleted."
        )
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Parse message count from command arguments
        message_count = config.bot_settings.default_summary_count
        if context.args and len(context.args) > 0:
            try:
                message_count = int(context.args[0])
                # Enforce maximum limit
                if message_count > config.bot_settings.max_summary_count:
                    await update.message.reply_text(
                        f"⚠️ Maximum {config.bot_settings.max_summary_count} messages allowed. "
                        f"Using {config.bot_settings.max_summary_count} instead."
                    )
                    message_count = config.bot_settings.max_summary_count
                elif message_count < 1:
                    await update.message.reply_text("⚠️ Please specify a positive number of messages.")
                    return
            except ValueError:
                await update.message.reply_text("⚠️ Please provide a valid number.")
                return
        
        # Send "thinking" message
        status_msg = await update.message.reply_text(
            f"🤔 Analyzing last {message_count} messages..."
        )
        
        try:
            # Retrieve messages from database
            messages = await self.message_store.get_recent_messages(chat_id, message_count)
            
            if not messages:
                await status_msg.edit_text(
                    "📭 No messages found to summarize. I only started logging messages "
                    "after being added to this chat."
                )
                return
            
            # Clean messages
            cleaned_messages = self.text_cleaner.clean_messages(messages)
            
            if not cleaned_messages:
                await status_msg.edit_text(
                    "📭 No meaningful messages found to summarize (only system messages or media)."
                )
                return
            
            # Get user's preferred style from database
            style_name = await self.message_store.get_user_setting(
                user_id, 
                'summary_style', 
                SummaryStyle.PROFESSIONAL.value
            )
            # Convert string to SummaryStyle enum
            try:
                style = SummaryStyle(style_name)
            except (ValueError, KeyError):
                style = SummaryStyle.PROFESSIONAL
            
            # Generate summary
            await status_msg.edit_text("✨ Generating summary...")
            summary = await self.llm_provider.summarize(cleaned_messages, style)
            
            # Send summary
            summary_text = (
                f"📊 Summary of last {len(messages)} messages ({style.value} style)\n\n"
                f"{summary}"
            )
            
            # Try to send with HTML first, fallback to plain text if parsing fails
            try:
                await status_msg.edit_text(summary_text, parse_mode='HTML')
            except Exception as html_error:
                # If HTML parsing fails, send as plain text
                logger.warning(f"HTML parsing failed, sending as plain text: {html_error}")
                await status_msg.edit_text(summary_text)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await status_msg.edit_text(
                f"❌ Error generating summary: {str(e)}\n\n"
                "Please try again or contact support."
            )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        
        # Get current style from database
        style_name = await self.message_store.get_user_setting(
            user_id, 
            'summary_style', 
            SummaryStyle.PROFESSIONAL.value
        )
        try:
            current_style = SummaryStyle(style_name)
        except (ValueError, KeyError):
            current_style = SummaryStyle.PROFESSIONAL
        
        # Create inline keyboard with style options
        keyboard = [
            [
                InlineKeyboardButton("👔 Professional", callback_data=f"style_{SummaryStyle.PROFESSIONAL.name}"),
                InlineKeyboardButton("😄 Funny", callback_data=f"style_{SummaryStyle.FUNNY.name}")
            ],
            [
                InlineKeyboardButton("📈 Executive", callback_data=f"style_{SummaryStyle.EXECUTIVE.name}"),
                InlineKeyboardButton("🔧 Technical", callback_data=f"style_{SummaryStyle.TECHNICAL.name}")
            ],
            [
                InlineKeyboardButton("💬 Casual", callback_data=f"style_{SummaryStyle.CASUAL.name}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚙️ <b>Settings</b>\n\n"
            f"Current style: <b>{current_style.value}</b>\n\n"
            "Choose your preferred summary style:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if query.data.startswith("style_"):
            style_name = query.data.replace("style_", "")
            style = SummaryStyle[style_name]
            
            # Save user settings to database
            await self.message_store.save_user_setting(user_id, 'summary_style', style.value)
            
            await query.edit_message_text(
                f"✅ Summary style updated to: <b>{style.value}</b>\n\n"
                f"Your preference has been saved and will persist across bot restarts!\n\n"
                f"Use /summary to generate a summary in this style!",
                parse_mode='HTML'
            )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        chat_id = update.effective_chat.id
        
        stats = await self.message_store.get_chat_statistics(chat_id)
        
        if not stats or stats.get('total_messages', 0) == 0:
            await update.message.reply_text(
                "📭 No statistics available yet. I'll start collecting data "
                "from messages sent after I was added to this chat."
            )
            return
        
        stats_text = (
            "📊 <b>Chat Statistics</b>\n\n"
            f"• Total messages: <b>{stats['total_messages']}</b>\n"
            f"• Unique users: <b>{stats['unique_users']}</b>\n"
            f"• First message: {stats.get('first_message', 'N/A')}\n"
            f"• Latest message: {stats.get('last_message', 'N/A')}\n\n"
            f"Messages are retained for {config.storage_settings.message_retention_days} days."
        )
        await update.message.reply_text(stats_text, parse_mode='HTML')
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages (for logging)"""
        if not update.message or not update.message.text:
            return
        
        message = update.message
        
        # Prepare message data
        message_data = {
            'chat_id': message.chat_id,
            'message_id': message.message_id,
            'user_id': message.from_user.id if message.from_user else None,
            'username': message.from_user.username or message.from_user.first_name if message.from_user else "Unknown",
            'text': message.text or '',
            'timestamp': message.date,
            'has_photo': bool(message.photo),
            'has_video': bool(message.video),
            'has_document': bool(message.document),
            'caption': message.caption or ''
        }
        
        # Store message in database
        await self.message_store.store_message(message_data)
