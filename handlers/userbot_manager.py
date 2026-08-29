import os
import asyncio
import logging
from pyrogram import Client
from configs import Config
from handlers.database import db

logger = logging.getLogger(__name__)

# Dictionary to store active userbot instances: user_id -> Client
active_userbots = {}

async def register_userbot_handlers(userbot: Client, user_id: int, bot_client: Client):
    """
    Registers disappearing/view-once media handlers on the userbot client.
    Import inside function to avoid circular imports.
    """
    from handlers.disappearing_media import handle_disappearing_media

    @userbot.on_message()
    async def _userbot_msg_handler(client: Client, message):
        await handle_disappearing_media(client, message, user_id, bot_client)

async def start_userbot(user_id: int, session_string: str, bot_client: Client = None) -> bool:
    """
    Starts a userbot client for a given user_id using session_string.
    """
    if user_id in active_userbots:
        try:
            await active_userbots[user_id].stop()
        except Exception:
            pass
        del active_userbots[user_id]

    try:
        userbot = Client(
            name=f"userbot_{user_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=session_string,
            in_memory=True
        )
        await userbot.start()

        if bot_client:
            await register_userbot_handlers(userbot, user_id, bot_client)

        active_userbots[user_id] = userbot
        logger.info(f"Userbot started successfully for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to start userbot for user {user_id}: {e}")
        return False

async def stop_userbot(user_id: int):
    """
    Stops and removes an active userbot instance.
    """
    if user_id in active_userbots:
        try:
            await active_userbots[user_id].stop()
        except Exception as e:
            logger.error(f"Error stopping userbot for {user_id}: {e}")
        del active_userbots[user_id]
        return True
    return False

async def start_all_userbots(bot_client: Client):
    """
    Retrieves all stored sessions from DB on bot startup and starts userbots.
    """
    sessions = await db.get_all_sessions()
    logger.info(f"Loading {len(sessions)} userbot session(s) from database...")
    for item in sessions:
        u_id = item.get("user_id")
        s_str = item.get("session_string")
        if u_id and s_str:
            asyncio.create_task(start_userbot(u_id, s_str, bot_client))
