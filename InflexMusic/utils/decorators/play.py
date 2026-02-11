import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from InflexMusic import YouTube, app
from InflexMusic.misc import SUDOERS
from InflexMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from InflexMusic.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_GROUP, adminlist
from strings import get_string

links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Necə düzəltmək olar ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} hal-hazırda texniki işlər altındadır. Ətraflı məlumat üçün <a href={SUPPORT_GROUP}>dəstək qrupu</a>na daxil olun.",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except:
            pass

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message else None
        )

        url = await YouTube.url(message)
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_text(
                    text=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                if message.from_user.id not in admins:
                    return await message.reply_text(_["play_4"])

        video = True if (
            message.command[0][0] == "v" or
            "-v" in message.text or
            (len(message.command[0]) > 1 and message.command[0][1] == "v")
        ) else None

        fplay = True if message.command[0][-1] == "e" else None

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                get = await app.get_chat_member(chat_id, userbot.id)
                if get.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention, userbot.id, userbot.name, userbot.username
                        )
                    )
            except UserNotParticipant:
                try:
                    if chat_id in links:
                        invitelink = links[chat_id]
                    elif message.chat.username:
                        invitelink = f"https://t.me/{message.chat.username}"
                    else:
                        invitelink = await app.export_chat_invite_link(chat_id)

                    links[chat_id] = invitelink
                    myu = await message.reply_text(_["call_4"].format(app.mention))

                    try:
                        await asyncio.sleep(1)
                        await userbot.join_chat(invitelink)
                        await asyncio.sleep(1)
                        await myu.edit(_["call_5"].format(app.mention))
                    except InviteRequestSent:
                        try:
                            await app.approve_chat_join_request(chat_id, userbot.id)
                            await asyncio.sleep(1)
                            await myu.edit(_["call_5"].format(app.mention))
                        except Exception as e:
                            return await message.reply_text(
                                _["call_3"].format(app.mention, type(e).__name__)
                            )
                    except UserAlreadyParticipant:
                        pass
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )

                except ChatAdminRequired:
                    return await message.reply_text(_["call_1"])
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(app.mention, type(e).__name__)
                    )
            except ChatAdminRequired:
                return await message.reply_text(_["call_1"])
            except Exception as e:
                return await message.reply_text(
                    _["call_3"].format(app.mention, type(e).__name__)
                )

        return await command(
            client, message, _, chat_id, video, channel, playmode, url, fplay
        )

    return wrapper
