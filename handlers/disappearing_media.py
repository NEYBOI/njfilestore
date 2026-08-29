# (c) @LazyDeveloperr

import os
import asyncio
import logging
from pyrogram import Client, enums
from pyrogram.types import Message
from configs import Config

logger = logging.getLogger(__name__)

async def handle_disappearing_media(userbot: Client, message: Message, user_id: int, bot_client: Client):
    """
    Handles incoming or replied-to messages in private chats for userbot instance.
    Detects view-once, self-destruct (TTL), or replied media in DMs and saves permanent copies.
    """
    if not message or message.chat.type != enums.ChatType.PRIVATE:
        return

    # Determine if this message is a reply sent by the logged-in user in DM
    is_reply_trigger = False
    target_message = None

    if message.outgoing and message.reply_to_message:
        is_reply_trigger = True
        target_message = message.reply_to_message
    elif not message.outgoing:
        # Check if incoming message is a view-once / self-destruct media
        target_message = message

    if not target_message:
        return

    # Check for photo, video, voice, video_note, document
    media = (
        target_message.photo or
        target_message.video or
        target_message.voice or
        target_message.video_note or
        target_message.document or
        target_message.audio
    )

    if not media:
        return

    # Check if media has TTL / self-destruct property or if user explicitly triggered save via reply
    ttl_seconds = getattr(target_message, "ttl_seconds", None) or getattr(media, "ttl_seconds", None)
    is_view_once = bool(ttl_seconds)

    # Save if it's explicitly triggered by user reply OR if it's an incoming view-once / disappearing media
    if not (is_reply_trigger or (is_view_once and Config.AUTO_SAVE_VIEW_ONCE)):
        return

    try:
        sender_name = target_message.from_user.first_name if target_message.from_user else "Unknown User"
        sender_id = target_message.from_user.id if target_message.from_user else "Unknown"
        caption = (
            f"📥 **Saved Disappearing Media**\n\n"
            f"👤 **From:** {sender_name} (`{sender_id}`)\n"
            f"⏱ **TTL / Self-Destruct:** `{ttl_seconds if ttl_seconds else 'N/A (Saved via reply)'}`"
        )

        # Download media locally
        file_path = await userbot.download_media(target_message)
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Failed to download media from message {target_message.id}")
            return

        # 1. Deliver saved media to User's PM via Telegram Bot
        if bot_client:
            try:
                if target_message.photo:
                    await bot_client.send_photo(chat_id=user_id, photo=file_path, caption=caption)
                elif target_message.video:
                    await bot_client.send_video(chat_id=user_id, video=file_path, caption=caption)
                elif target_message.audio:
                    await bot_client.send_audio(chat_id=user_id, audio=file_path, caption=caption)
                elif target_message.voice:
                    await bot_client.send_voice(chat_id=user_id, voice=file_path, caption=caption)
                else:
                    await bot_client.send_document(chat_id=user_id, document=file_path, caption=caption)
            except Exception as e:
                logger.error(f"Error sending media to bot PM for user {user_id}: {e}")

        # 2. Save media to DB Channel if configured
        if bot_client and Config.DB_CHANNEL:
            try:
                if target_message.photo:
                    await bot_client.send_photo(chat_id=Config.DB_CHANNEL, photo=file_path, caption=f"#SAVED_MEDIA\nUser ID: `{user_id}`\n" + caption)
                elif target_message.video:
                    await bot_client.send_video(chat_id=Config.DB_CHANNEL, video=file_path, caption=f"#SAVED_MEDIA\nUser ID: `{user_id}`\n" + caption)
                else:
                    await bot_client.send_document(chat_id=Config.DB_CHANNEL, document=file_path, caption=f"#SAVED_MEDIA\nUser ID: `{user_id}`\n" + caption)
            except Exception as e:
                logger.error(f"Error sending media to DB_CHANNEL: {e}")

        # 3. Save media to User's Saved Messages via Userbot
        if Config.SAVE_TO_SAVED_MESSAGES:
            try:
                if target_message.photo:
                    await userbot.send_photo(chat_id="me", photo=file_path, caption=caption)
                elif target_message.video:
                    await userbot.send_video(chat_id="me", video=file_path, caption=caption)
                else:
                    await userbot.send_document(chat_id="me", document=file_path, caption=caption)
            except Exception as e:
                logger.error(f"Error sending media to Saved Messages for user {user_id}: {e}")

        # Remove temp local file
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logger.error(f"Exception handling disappearing media: {e}")
