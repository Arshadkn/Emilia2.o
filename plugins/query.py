import asyncio, re, ast, math, logging, random, pyrogram
from datetime import datetime
from pytz import timezone

# pyrogram functions
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums 
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid


from Script import script
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_all_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters
from plugins.helper.admin_check import admin_fliter

# image editor tools
from image.edit_1 import bright, mix, black_white, g_blur, normal_blur, box_blur
from image.edit_2 import circle_with_bg, circle_without_bg, sticker, edge_curved, contrast, sepia_mode, pencil, cartoon                             
from image.edit_3 import green_border, blue_border, black_border, red_border
from image.edit_4 import rotate_90, rotate_180, rotate_270, inverted, round_sticker, removebg_white, removebg_plain, removebg_sticker
from image.edit_5 import normalglitch_1, normalglitch_2, normalglitch_3, normalglitch_4, normalglitch_5, scanlineglitch_1, scanlineglitch_2, scanlineglitch_3, scanlineglitch_4, scanlineglitch_5

# configuration
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, PICS, IMDB, PM_IMDB, SINGLE_BUTTON, PROTECT_CONTENT, \
    SPELL_CHECK_REPLY, IMDB_TEMPLATE, IMDB_DELET_TIME, START_MESSAGE, PMFILTER, G_FILTER, BUTTON_LOCK, BUTTON_LOCK_TEXT, SHORT_URL, SHORT_API

TIMEZONE = (os.environ.get("TIMEZONE", "Asia/Kolkata"))
curr = datetime.now(timezone(TIMEZONE))
date = curr.strftime('%d-%B-%Y')
time = curr.strftime('%I:%M:%S %p')
day = curr.strftime("%A")
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)



@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return
        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Buddy Don't Touch Others Property 😁", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "𝙲𝙾𝙽𝙽𝙴𝙲𝚃"
            cb = "connectcb"
        else:
            stat = "𝙳𝙸𝚂𝙲𝙾𝙽𝙽𝙴𝙲𝚃"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("𝙳𝙴𝙻𝙴𝚃𝙴", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("𝙱𝙰𝙲𝙺", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"𝙶𝚁𝙾𝚄𝙿 𝙽𝙰𝙼𝙴 :- **{title}**\n𝙶𝚁𝙾𝚄𝙿 𝙸𝙳 :- `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))
        
        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"𝙲𝙾𝙽𝙽𝙴𝙲𝚃𝙴𝙳 𝚃𝙾 **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode="md")
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]        
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)       
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "galert" in query.data:
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]             
        reply_text, btn, alerts, fileid = await find_gfilter("gfilters", keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    
    if query.data.startswith("pmfile"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(mention=query.from_user.mention, file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)                                                                                                      
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"    
        try:                  
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                return await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "pmfilep" else False                    
                )                       
        except Exception as e:
            await query.answer(f"⚠️ Error {e}", show_alert=True)
        
    if query.data.startswith("file"):        
        ident, req, file_id = query.data.split("#")
        if BUTTON_LOCK.strip().lower() in ["true", "yes", "1", "enable", "y"]:
            if int(req) not in [query.from_user.id, 0]:
                return await query.answer(BUTTON_LOCK_TEXT.format(query=query.from_user.first_name), show_alert=True)             
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(mention=query.from_user.mention, file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)                               
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"        
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
     
      
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart Okay", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
               f_caption = CUSTOM_FILE_CAPTION.format(mention=query.from_user.mention, file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)  
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
  
     

    elif query.data == "pages":
        await query.answer("🤨 Curiosity is a little more, isn't it? 😁", show_alert=True)
    elif query.data == "howdl":
        try:
            await query.answer(script.HOW_TO_DOWNLOAD.format(query.from_user.first_name), show_alert=True)
        except:
            await query.message.edit(script.HOW_TO_DOWNLOAD.format(query.from_user.first_name))


    elif query.data == "start":                        
        buttons = [[
            InlineKeyboardButton("💢 ᴄʟɪᴄᴋ ᴛᴏ ᴠɪᴇᴡ ᴍᴏʀᴇ ʙᴜᴛᴛᴏɴs 💢", callback_data="help")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), START_MESSAGE.format(user=query.from_user.mention, bot=temp.B_LINK), enums.ParseMode.HTML),
            reply_markup=reply_markup,
           
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('🔕 ᴄʟɪᴄᴋ ᴛᴏ ᴄʟᴏsᴇ ᴛʜɪs ʙᴜᴛᴛᴏɴs 🔕', callback_data='start')
            ],[
            InlineKeyboardButton('👨‍🔧 ᴏᴡɴᴇʀ', callback_data='extra'),            
            InlineKeyboardButton('🎬 ᴄʜᴀɴɴᴇʟ', url='https://t.me/CmRips')
            ],[
            InlineKeyboardButton('👥 ɢʀᴏᴜᴘ', url='https://t.me/cenEma9'),
            InlineKeyboardButton('🔒 ᴄʟᴏsᴇ', callback_data='close_data')           
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)             
        await query.edit_message_media(  
            InputMediaPhoto(random.choice(PICS), script.START_TXT.format(query.from_user.mention), enums.ParseMode.HTML),
            reply_markup=reply_markup,           
        )
    elif query.data == "about":
        buttons= [[
            InlineKeyboardButton('❣️ 𝚂𝙾𝚄𝚁𝙲𝙴 𝙲𝙾𝙳𝙴 ❣️', callback_data='source')
            ],[
            InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start'),
            InlineKeyboardButton('🔐 𝙲𝙻𝙾𝚂𝙴 🔐', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ABOUT_TXT.format(temp.B_NAME), enums.ParseMode.HTML),
            reply_markup=reply_markup,           
        )
    elif query.data == "gxneopm":
        await query.answer("📵 ᴄᴏɴᴛᴀᴄᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ\n\n- ꜱᴇᴄᴛɪᴏɴ B206 - ꜱᴘᴀᴍ + ʙᴀɴ ⚠️\n\n- ꜱᴇᴄᴛɪᴏɴ Y8R6 - ꜱᴘᴀᴍ + ʀᴇᴘᴏʀᴛ 🉐\n\n🗽 ʙʏ Dᴇᴠɪɴ' [Oғғʟɪɴᴇ]", show_alert=True)

    elif query.data == "movieinfo":
        await query.answer("⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nᴀꜰᴛᴇʀ 30 ᴍɪɴᴜᴛᴇᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ\n\nɪꜰ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ꜱᴇᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ / sᴇʀɪᴇs ꜰɪʟᴇ, ʟᴏᴏᴋ ᴀᴛ ᴛʜᴇ ɴᴇxᴛ ᴘᴀɢᴇ\n\n© ᴄɪɴᴇᴍᴀᴄᴏᴍᴘᴀɴʏ", show_alert=True)

    elif query.data == "movss":
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ\n\nᴇxᴀᴍᴘʟᴇ : ᴋɢꜰ ᴄʜᴀᴘᴛᴇʀ 2  2022\n\n🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)\n\n©  ᴄɪɴᴇᴍᴀᴄᴏᴍᴘᴀɴʏ", show_alert=True)

    elif query.data == "moviis":  
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ\n\nᴇxᴀᴍᴘʟᴇ : ʟᴏᴋɪ S01 E01\n\n🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)\n\n© ᴄɪɴᴇᴍᴀᴄᴏᴍᴘᴀɴʏ", show_alert=True)   
        
    elif query.data == "banreo":
         await query.answer("⛔Reason : No reason Provided", show_alert=True)

    elif query.data == "neosub":
        await query.answer("അഥവാ ഗ്രൂപ്പ്‌ കോപ്പിറൈറ് കിട്ടി പോയാൽ.. പുതിയ ഗ്രൂപ്പ്‌ തുടങ്ങുമ്പോൾ ഇപ്പോൾ ജോയിൻ ആകുന്ന ചാനൽ വഴി ആയിരിക്കും അറിയിക്കുന്നത് 🤥",show_alert=True)
  
    elif query.data == "toime":
        await query.answer(f"⏰ Tɪᴍᴇ : {time}\n\n📆 Dᴀᴛᴇ : {date}\n\n⛅ Wᴇᴇᴋᴅᴀʏ : {day}\n\n©CɪɴᴇᴍᴀCᴏᴍᴘᴀɴʏ", show_alert=True)
    
    elif query.data == "malspell":
        btn = [[
            InlineKeyboardButton('🔍 ɢᴏᴏɢʟᴇ 🔎', url=f'https://google.com/search?q='),
            InlineKeyboardButton(' 🔍 ʏᴀɴᴅᴇx 🔎', url=f'https://yandex.com/search?text=')
        ],[
            InlineKeyboardButton("🇺🇸 ᴛʀᴀɴsʟᴀᴛᴇ ᴛᴏ ᴇɴɢʟɪꜱʜ 🇺🇸", callback_data="engspell")
        ]] 
        await query.message.edit_text(script.SPELL_CHECK_MAL, reply_markup=InlineKeyboardMarkup(btn))
    elif query.data == "engspell":
        btn = [[
            InlineKeyboardButton('🔍 ɢᴏᴏɢʟᴇ 🔎', url=f'https://google.com/search?q='),
            InlineKeyboardButton(' 🔍 ʏᴀɴᴅᴇx 🔎', url=f'https://yandex.com/search?text=')
        ],[
            InlineKeyboardButton("🇮🇳 ᴛʀᴀɴsʟᴀᴛᴇ ᴛᴏ ᴍᴀʟᴀʏᴀʟᴀᴍ 🇮🇳", callback_data="malspell")
        ]] 
        await query.message.edit_text(script.SPELL_CHECK_ENG, reply_markup=InlineKeyboardMarkup(btn))
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('SOURCE CODE', url='https://github.com/MrMKN/PROFESSOR-BOT')
            ],[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SOURCE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "restric":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.RESTRIC_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "image":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.IMAGE_TXT.format(temp.B_NAME), enums.ParseMode.HTML),            
            reply_markup=reply_markup,
        ) 
    elif query.data == "ytdl":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.YTDL, enums.ParseMode.HTML),            
            reply_markup=reply_markup,
        )  
    elif query.data == "sharetxt":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SHARE_TXT, enums.ParseMode.HTML),           
            reply_markup=reply_markup,
        )      
    elif query.data == "zombies":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ZOMBIES_TXT, enums.ParseMode.HTML),           
            reply_markup=reply_markup,
        )    
    elif query.data == "pin":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PIN_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "son":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.JSON_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "pastes":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PASTE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "pings":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PINGS_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "ttss":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.TTS_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "purges":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PURGE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.TELE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )             
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝙱𝚄𝚃𝚃𝙾𝙽𝚂', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.MANUELFILTER_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.BUTTON_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.AUTOFILTER_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.CONNECTION_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )   

    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('ᴄᴏɴᴛᴀᴄᴛ', callback_data='gxneopm'), 
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.EXTRAMOD_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )

    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('𝙶𝙻𝙾𝙱𝙰𝙻 𝙵𝙸𝙻𝚃𝙴𝚁', callback_data='gfill'),
            InlineKeyboardButton('𝚄𝚂𝙴𝚁 & 𝙲𝙷𝙰𝚃', callback_data='uschat')
            ],[
            InlineKeyboardButton('🔙 𝙱𝙰𝙲𝙺', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if query.from_user.id in ADMINS:
            await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.ADMIN_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
        else:
            await query.answer("Your Not Authorizer ⚠️", show_alert=True)

    elif query.data == "gfill":
        buttons = [[            
            InlineKeyboardButton('🔙 𝙱𝙰𝙲𝙺', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.G_FIL_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
        
    elif query.data == "uschat":
        buttons = [[            
            InlineKeyboardButton('🔙 𝙱𝙰𝙲𝙺', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.US_CHAT_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
       
    elif query.data == "carb":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.CARB_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )      
    elif query.data == "fond":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.FOND_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )       
    elif query.data == "newdata":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.FILE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.STATUS_TXT.format(total, users, chats, monsize, free), enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.STATUS_TXT.format(total, users, chats, monsize, free), enums.ParseMode.HTML),
            reply_markup=reply_markup,          
      )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))
        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return 
        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)
        settings = await get_settings(grpid)
        if settings is not None:
            buttons = [[
                InlineKeyboardButton('𝐅𝐈𝐋𝐓𝐄𝐑 𝐁𝐔𝐓𝐓𝐎𝐍', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('𝐒𝐈𝐍𝐆𝐋𝐄' if settings["button"] else '𝐃𝐎𝐔𝐁𝐋𝐄',  callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐁𝐎𝐓 𝐏𝐌', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["botpm"] else '🗑️ 𝐍𝐎', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],[                
                InlineKeyboardButton('𝐅𝐈𝐋𝐄 𝐒𝐄𝐂𝐔𝐑𝐄', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["file_secure"] else '🗑️ 𝐍𝐎',  callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐈𝐌𝐃𝐁', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["imdb"] else '🗑️ 𝐍𝐎', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐒𝐏𝐄𝐋𝐋 𝐂𝐇𝐄𝐂𝐊', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["spell_check"] else '🗑️ 𝐍𝐎', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐖𝐄𝐋𝐂𝐎𝐌𝐄', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["welcome"] else '🗑️ 𝐍𝐎', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')               
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)







