from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import SUPPORT_CHAT

async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group=filters.create(disabled_chat)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    buttons = [[
        InlineKeyboardButton('📵 Aᴅᴍɪɴ', url=f'https://t.me/adpsycho'), 
        InlineKeyboardButton(f'⚠️ Bᴀɴ Rᴇᴀsᴏɴ', 'banreo')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    ban = await db.get_ban_status(message.from_user.id)
    m=await message.reply_sticker("CAACAgUAAxkBAAEILFpkFHQXxRb5tWqOlEtyUIqu9qs_KAACJAAD046EI5b3vYsJLhc2LwQ")
    await message.reply(
          text=f'<code>Sorry Dude, You are Banned to use Me.My Admin Warned You to use my now You are Break My Rules That is Ban Reason Ask My Admin To Unban You\n\nക്ഷമിക്കണം സുഹൃത്തേ, നിങ്ങൾ എന്നെ ഉപയോഗിക്കുന്നതിന് വിലക്കപ്പെട്ടിരിക്കുന്നു. എന്റെ അഡ്മിൻ നിങ്ങൾക്ക് മുന്നറിയിപ്പ് നൽകി, ഇപ്പോൾ എന്റെ നിയമങ്ങൾ നിങ്ങൾ ലംഘിക്കുകയാണ്, അതാണ് വിലക്ക് കാരണം നിങ്ങളെ അൺബാൻ ചെയ്യാൻ എന്റെ അഡ്മിനോട് ആവശ്യപ്പെടുക</code>\n\n📜 Bᴀɴ Rᴇᴀsᴏɴ : {ban["ban_reason"]}', 
          reply_markup=reply_markup)
    
@Client.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot, message):
    buttons = [[
        InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    k = await message.reply(
        text=f"CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..\nReason : <code>{vazha['reason']}</code>.",
        reply_markup=reply_markup)
    try:
        await k.pin()
    except:
        pass
    await bot.leave_chat(message.chat.id)
