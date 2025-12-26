"""SQLite database for message persistence"""
import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MessageStore:
    """Asynchronous SQLite message store"""
    
    def __init__(self, db_path: str = "data/messages.db"):
        """
        Initialize message store
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    user_id INTEGER,
                    username TEXT,
                    text TEXT,
                    timestamp DATETIME NOT NULL,
                    is_system_message BOOLEAN DEFAULT 0,
                    has_photo BOOLEAN DEFAULT 0,
                    has_video BOOLEAN DEFAULT 0,
                    has_document BOOLEAN DEFAULT 0,
                    caption TEXT,
                    UNIQUE(chat_id, message_id)
                )
            """)
            
            # Create index for faster queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_timestamp 
                ON messages(chat_id, timestamp DESC)
            """)
            
            await db.commit()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    async def store_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Store a message in the database
        
        Args:
            message_data: Dictionary containing message information
        
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO messages 
                    (chat_id, message_id, user_id, username, text, timestamp,
                     is_system_message, has_photo, has_video, has_document, caption)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message_data.get('chat_id'),
                    message_data.get('message_id'),
                    message_data.get('user_id'),
                    message_data.get('username', 'Unknown'),
                    message_data.get('text', ''),
                    message_data.get('timestamp', datetime.now()),
                    message_data.get('is_system_message', False),
                    message_data.get('has_photo', False),
                    message_data.get('has_video', False),
                    message_data.get('has_document', False),
                    message_data.get('caption', '')
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False
    
    async def get_recent_messages(
        self, 
        chat_id: int, 
        limit: int = 20,
        before_timestamp: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent messages from a chat
        
        Args:
            chat_id: Chat ID to retrieve messages from
            limit: Maximum number of messages to retrieve
            before_timestamp: Only get messages before this timestamp
        
        Returns:
            List of message dictionaries
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if before_timestamp:
                    cursor = await db.execute("""
                        SELECT * FROM messages 
                        WHERE chat_id = ? AND timestamp < ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (chat_id, before_timestamp, limit))
                else:
                    cursor = await db.execute("""
                        SELECT * FROM messages 
                        WHERE chat_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (chat_id, limit))
                
                rows = await cursor.fetchall()
                
                # Convert to dictionaries and reverse order (oldest first)
                messages = [dict(row) for row in rows]
                messages.reverse()
                
                return messages
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    
    async def get_message_count(self, chat_id: int) -> int:
        """
        Get total message count for a chat
        
        Args:
            chat_id: Chat ID
        
        Returns:
            Number of messages
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM messages WHERE chat_id = ?
                """, (chat_id,))
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0
    
    async def clean_old_messages(self, retention_days: int = 30):
        """
        Clean up old messages beyond retention period
        
        Args:
            retention_days: Number of days to retain messages
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM messages WHERE timestamp < ?
                """, (cutoff_date,))
                await db.commit()
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old messages")
        except Exception as e:
            logger.error(f"Error cleaning old messages: {e}")
    
    async def get_chat_statistics(self, chat_id: int) -> Dict[str, Any]:
        """
        Get statistics for a chat
        
        Args:
            chat_id: Chat ID
        
        Returns:
            Dictionary with statistics
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total messages
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM messages WHERE chat_id = ?
                """, (chat_id,))
                total_messages = (await cursor.fetchone())[0]
                
                # Unique users
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM messages 
                    WHERE chat_id = ? AND user_id IS NOT NULL
                """, (chat_id,))
                unique_users = (await cursor.fetchone())[0]
                
                # First and last message timestamps
                cursor = await db.execute("""
                    SELECT MIN(timestamp), MAX(timestamp) FROM messages 
                    WHERE chat_id = ?
                """, (chat_id,))
                first_msg, last_msg = await cursor.fetchone()
                
                return {
                    'total_messages': total_messages,
                    'unique_users': unique_users,
                    'first_message': first_msg,
                    'last_message': last_msg
                }
        except Exception as e:
            logger.error(f"Error getting chat statistics: {e}")
            return {}
