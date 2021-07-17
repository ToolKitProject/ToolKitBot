from aiogram.utils.markdown import hbold as b
from aiogram.utils.markdown import hcode as c
from aiogram.utils.markdown import hitalic as i
from aiogram.utils.markdown import hlink as l
from aiogram.utils.markdown import text as t

cancel = "\n/cancel - to cancel"


class errors:
    class restrict:
        pass

    class argument_error:
        ArgumentError = "⚠ Invalid argument"

        incorrect = f'Argument "{b("{arg_name}")}" incorrect'
        required = f'Argument "{b("{arg_name}")}" required'

    until = "If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever. "
    UntilWaring = f"❗ {until}"

    CommandNotFound = "⚠ Command not found"
    UserNotFound = "⚠ User not found"
    HasNotPermission = "⚠ You don't have the permission"
    EmptyOwns = "⚠ You do not own chats"
    TypeError = "⚠ Wrong type"
    AlreadyExists = "⚠ Already exists"
    NotReply = "⚠ Not replied"
    BotHasNotPermission = "⚠ The bot has no or not enough rights"
    BackError = "⚠ Back error"
    PollCheck = "⚠ Not enough votes"

class private:
    start_text = "Hi, I am a ToolKit bot and I am dedicated to everything you can imagine 😜 \n" + \
                 "What I can do 😊 \n" + \
                 "┣ Edit photo 🌅 \n" + \
                 "┣ Moderate groups ⚙️ \n" + \
                 "┣ Decrypt voice 🎤 \n" + \
                 "┣ Generate voice 🎙 \n" + \
                 "┗ Generate memes 😎"

    class settings:
        chat_loading = "🕒 Please wait,chats is loading"
        sticker = "1⃣ Send me sticker" + cancel
        text = "1⃣ Send me text" + cancel

        command = "2⃣ Send me command"


class chat:
    _perm = "┣ /ban /unban ⛔ \n" + \
            "┣ /mute /unmute 🔇 \n" + \
            "┣ /purge 🗑\n" + \
            "┗ /kick ⚠"

    start_text = "Hello i am ToolKit bot\n" + \
                 "What i can do this chat\n" + \
                 "┣ Moderate ⚙️ \n" + \
                 "┗ Decrypt voice messages 🎤 \n" + \
                 " \n" + \
                 "For administration commands to work, please grant these rights\n" + \
                 "┣ Delete messages ⚠ \n" + \
                 "┣ Invite links 🔗 \n" + \
                 "┗ Ban user ⛔"
    promote_admin = "The bot now <b>has</b> administrator rights \n" + \
                    "Now you <b>can</b> use commands like \n" + \
                    _perm
    restrict_admin = "The bot now <b>hasn't</b> administrator rights \n" + \
                     "Now you <b>can't</b> use commands like \n" + \
                     _perm

    class admin:
        reason = f"Reason ❓ - {c('{reason}')} \n"
        admin = f"Moderator 👤 - {i('{admin}')} \n"
        until = f"Until ⌛ - {b('{until}')} \n"

        unmute = "{user} unmuted 🔈 \n" + reason + admin
        multi_unmute = unmute
        unmute_poll = "🔈 Unmute - {user} ?"

        mute = "{user} muted 🔇 \n" + reason + admin + until
        multi_mute = mute
        mute_poll = "🔇 Mute - {user} ?"

        kick = "{user} kicked out ⚠ \n" + reason + admin
        multi_kick = kick
        kick_poll = "⚠ Kick out - {user} ?"

        unban = "{user} unbanned ✅ \n" + reason + admin
        multi_unban = unban
        unban_poll = "✅ Unban - {user} ?"

        ban = "{user} banned ⛔ \n" + reason + admin + until
        multi_ban = ban
        ban_poll = "⛔ Ban - {user} ?"

        options_poll = ["✅ Yes", "⛔ No "]

        forever = "February 31, 1970"
        reason_empty = "Without any reasons"

        purge = "🗑 Chat purged of {count} messages"


class help:
    users = f'👥 Mentions (@username,{l(f"Jack Jackson", "t.me/username")} or reply) \n'
    until = '⏳ Date[s|m|h|d|M|y] (1m 30s or 1M) \n'
    reason = '❔ "Reason" (Yes in the quote) \n'
    poll = '📈 Make a poll (-p --poll)'

    ban = "⛔ /ban \n" + users + until + reason + poll
    unban = "✅ /unban \n" + users + reason + poll
    kick = "⚠ /kick \n" + users + reason + poll
    mute = "🔇 /mute \n" + users + until + reason + poll
    unmute = "🔈 /unmute \n" + users + reason + poll

    count = "\n🔢 Count (2 - 1000)"
    reply = "\n⤴ Reply to delete above"

    purge = "🗑 /purge" + count + reply
