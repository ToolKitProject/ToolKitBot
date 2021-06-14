from aiogram.utils.markdown import hbold as b
from aiogram.utils.markdown import hcode as c
from aiogram.utils.markdown import hitalic as i
from aiogram.utils.markdown import hlink as l
from aiogram.utils.markdown import text as t


cancel = "\n/cancel - to cancel"


class errors:
    class command:
        CommandNotFound = "⚠ Command not found"
        ArgumentError = "⚠ Invalid argument"
        required = "{arg} required"

    until = "If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever."
    UntilWaring = f"❗ {until}"

    CommandNotFound = "⚠ Command not found"
    UserNotFound = "⚠ User not found"
    ArgumentError = "⚠ Invalid argument"
    HasNotPermission = "⚠ You have not not permission"
    EmptyOwns = "⚠ You do not own chats"
    TypeError = "⚠ Wrong type"
    AlreadyExists = "⚠ Already exists"
    NotReply = "⚠ Not replied"
    BotHasNotPermission = "⚠ The bot has no or not enough rights"
    BackError = "⚠ Back error"


class private:
    start_text = "Hi, I am a ToolKit bot and I am dedicated to everything you can imagine 😜 \n" +\
                 "What I can do 😊 \n" +\
                 "┣ Edit photo 🌅 \n" +\
                 "┣ Moderate groups ⚙️ \n" +\
                 "┣ Decrypt voice 🎤 \n" +\
                 "┣ Generate voice 🎙 \n" +\
                 "┗ Generate memes 😎"

    class settings:
        chat_loading = "🕒 Please wait,chats is loading"
        sticker = "1⃣ Send me sticker" + cancel
        text = "1⃣ Send me text" + cancel

        command = "2⃣ Send me command"


class chat:
    _perm = "┣ /ban /unban ⛔ \n" +\
            "┣ /mute /unmute 🔇 \n" +\
            "┣ /purge 🗑\n" +\
            "┗ /kick ⚠"

    start_text = "Hello i am ToolKit bot\n" +\
                 "What i can do this chat\n" +\
                 "┣ Moderate ⚙️ \n" +\
                 "┗ Decrypt voice messages 🎤 \n" +\
                 " \n" +\
                 "For administration commands to work, please grant these rights\n" +\
                 "┣ Delete messages ⚠ \n" +\
                 "┣ Invite links 🔗 \n" +\
                 "┗ Ban user ⛔"
    promote_admin = "The bot now <b>has</b> administrator rights \n" +\
                    "Now you <b>can</b> use commands like \n" +\
                    _perm
    restrict_admin = "The bot now <b>hasn't</b> administrator rights \n" +\
                     "Now you <b>can't</b> use commands like \n" +\
                     _perm

    class admin:
        reason = f"Reason ❔ - {c('{reason}')} \n"
        admin = f"Moderator 👤 - {i('{admin}')} \n"
        until = f"Until ⌛ - {b('{until}')} \n"

        unmute = "{user} unmuted 🔈 \n" + reason + admin
        multi_unmute = unmute

        mute = "{user} muted 🔇 \n" + reason + admin + until
        multi_mute = mute

        kick = "{user} kicked out ⚠ \n" + reason + admin
        multi_kick = kick

        unban = "{user} unbanned ✅ \n" + reason + admin
        multi_unban = unban

        ban = "{user} banned ⛔ \n" + reason + admin + until
        multi_ban = ban

        forever = "February 31, 1970"
        reason_empty = "Without reasons"

        purge = "🗑 Chat purged of {count} messages"


class help:
    users = f"\n👥 Mentions (@username,{l('Jack Jackson','t.me/username')} or reply)"
    until = "\n⏳ Date[s|m|h|d|M|y] (1m 30s, 1M)"
    reason = "\n❔ \"Reason\" (Yes in the quote)"
    # revoke_admin = "\n🚫 -r revoke admin"
    # delete_all_message = "\n🗑 -d delete all messages"
    revoke_admin = ""
    delete_all_message = ""

    ban = "⛔ /ban" + users + until + reason + revoke_admin + delete_all_message
    unban = "✅ /unban" + users + reason
    kick = "⚠ /kick" + users + reason + revoke_admin + delete_all_message
    mute = "🔇 /mute" + users + until + reason + delete_all_message
    unmute = "🔈 /unmute" + users + reason

    count = "\n🔢 Count (0 - 1000)"
    reply = "\n⤴ Reply to delete above"

    purge = "🗑 /purge" + count + reply
