# (c) @LazyDeveloperr

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from configs import Config
from handlers.database import db
from handlers.userbot_manager import start_userbot, stop_userbot

# In-memory user state dictionary for login steps
# format: user_id -> { step, client, phone_number, phone_code_hash }
login_states = {}

async def handle_login_command(bot: Client, message: Message):
    user_id = message.from_user.id

    # Check if user already has an active session
    existing_session = await db.get_user_session(user_id)
    if existing_session:
        await message.reply_text(
            "🔑 **You are already logged in!**\n\n"
            "If you want to log in with another account or reset your session, send `/logout` first.",
            quote=True
        )
        return

    # Prompt user for phone number or string session
    login_states[user_id] = {"step": "AWAITING_INPUT"}
    await message.reply_text(
        "📱 **Telegram Login Setup**\n\n"
        "Please send your **Phone Number** with country code (e.g., `+1234567890`)\n"
        "OR paste your Pyrogram **Session String** directly.\n\n"
        "To cancel at any time, send `/cancel`.",
        quote=True
    )

async def handle_logout_command(bot: Client, message: Message):
    user_id = message.from_user.id
    existing_session = await db.get_user_session(user_id)
    if not existing_session:
        await message.reply_text("❌ You don't have an active session logged in.", quote=True)
        return

    await stop_userbot(user_id)
    await db.delete_user_session(user_id)
    await message.reply_text("✅ **Logged out successfully!** Your session has been removed.", quote=True)

async def handle_cancel_command(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in login_states:
        client_obj = login_states[user_id].get("client")
        if client_obj:
            try:
                await client_obj.disconnect()
            except Exception:
                pass
        del login_states[user_id]
        await message.reply_text("❌ Login process cancelled.", quote=True)
    else:
        await message.reply_text("No active login process to cancel.", quote=True)

async def handle_login_steps(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in login_states:
        return

    state = login_states[user_id]
    step = state.get("step")
    text = message.text.strip()

    if text == "/cancel":
        await handle_cancel_command(bot, message)
        return

    if step == "AWAITING_INPUT":
        # Check if text is a Session String (usually ~350+ chars)
        if len(text) > 100:
            msg = await message.reply_text("⏳ Verifying session string...", quote=True)
            success = await start_userbot(user_id, text, bot)
            if success:
                await db.set_user_session(user_id, text)
                del login_states[user_id]
                await msg.edit("✅ **Session string added successfully!**\nYour view-once & disappearing media saver is now active!")
            else:
                await msg.edit("❌ Invalid Session String. Please check and try `/login` again.")
            return

        # Otherwise treat input as Phone Number
        phone_number = text.replace(" ", "")
        msg = await message.reply_text(f"⏳ Sending verification code to `{phone_number}`...", quote=True)

        user_client = Client(
            name=f"temp_user_{user_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            in_memory=True
        )

        try:
            await user_client.connect()
            code_info = await user_client.send_code(phone_number)

            login_states[user_id] = {
                "step": "AWAITING_CODE",
                "client": user_client,
                "phone_number": phone_number,
                "phone_code_hash": code_info.phone_code_hash
            }

            await msg.edit(
                "📩 **Verification code sent!**\n\n"
                "Please enter the code you received on Telegram (e.g. `1 2 3 4 5` or `12345`).\n"
                "_Tip: Send the code as numbers with spaces like `1 2 3 4 5` if Telegram blocks sending raw numbers!_"
            )
        except Exception as e:
            await user_client.disconnect()
            del login_states[user_id]
            await msg.edit(f"❌ Failed to send verification code:\n`{e}`\n\nPlease try `/login` again.")

    elif step == "AWAITING_CODE":
        phone_code = text.replace(" ", "").replace("-", "")
        user_client = state["client"]
        phone_number = state["phone_number"]
        phone_code_hash = state["phone_code_hash"]

        msg = await message.reply_text("⏳ Verifying code...", quote=True)

        try:
            await user_client.sign_in(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=phone_code
            )

            # Export session string
            session_string = await user_client.export_session_string()
            await db.set_user_session(user_id, session_string)

            # Start Userbot listener
            await start_userbot(user_id, session_string, bot)

            await user_client.disconnect()
            del login_states[user_id]
            await msg.edit("🎉 **Login Successful!**\n\nYour view-once and disappearing media saver is now active 24/7!")

        except SessionPasswordNeeded:
            login_states[user_id]["step"] = "AWAITING_PASSWORD"
            await msg.edit(
                "🔒 **Two-Step Verification Enabled**\n\n"
                "Please enter your 2FA password to complete login."
            )
        except (PhoneCodeInvalid, PhoneCodeExpired) as e:
            await msg.edit(f"❌ Invalid or expired code (`{e}`). Please try entering the code again or send `/cancel`.")
        except Exception as e:
            await user_client.disconnect()
            del login_states[user_id]
            await msg.edit(f"❌ Login failed:\n`{e}`\n\nPlease try `/login` again.")

    elif step == "AWAITING_PASSWORD":
        password = text
        user_client = state["client"]
        msg = await message.reply_text("⏳ Verifying 2FA password...", quote=True)

        try:
            await user_client.check_password(password)

            # Export session string
            session_string = await user_client.export_session_string()
            await db.set_user_session(user_id, session_string)

            # Start Userbot listener
            await start_userbot(user_id, session_string, bot)

            await user_client.disconnect()
            del login_states[user_id]
            await msg.edit("🎉 **Login Successful!**\n\nYour view-once and disappearing media saver is now active 24/7!")

        except PasswordHashInvalid:
            await msg.edit("❌ Incorrect password. Please try entering your password again or send `/cancel`.")
        except Exception as e:
            await user_client.disconnect()
            del login_states[user_id]
            await msg.edit(f"❌ Verification failed:\n`{e}`\n\nPlease try `/login` again.")
