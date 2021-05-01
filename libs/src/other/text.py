from aiogram.utils.markdown import hlink as l

cancel = "\n/cancel - to cancel"


class errors:
    until = "If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever."
    UntilWaring = f"❗ {until}"

    CommandNotFound = "⚠ Command not found"
    UserNotFound = "⚠ User not found"
    ArgumentError = "⚠ Invalid argument"
    HasNotPermission = "⚠ You don't have the permission"
    EmptyOwns = "⚠ You do not own chats"
    TypeError = "⚠ Wrong type"
    AlreadyExists = "⚠ Already exists"
    NotReply = "⚠ Not replied"


class private:
    class settings:
        chat_loading = "🕒 Please wait,chats is loading"
        sticker = "1⃣ Send me sticker" + cancel
        text = "1⃣ Send me text" + cancel
        command = "2⃣ Send me command"


class chat:
    class admin:
        reason = "Reason - {reason} \n"
        admin = "Moderator - {admin} \n"
        until = "Until - {until} \n"

        unmute = "{users} unmuted \n" + reason + admin
        multi_unmute = unmute

        mute = "{users} muted \n" + reason + admin + until
        multi_mute = mute

        kick = "{users} kicked out \n" + reason + admin
        multi_kick = kick

        unban = "{users} unbanned \n" + reason + admin
        multi_unban = unban

        ban = "{users} banned \n" + reason + admin + until
        multi_ban = ban

        forever = "February 31, 1970"
        reason_empty = "Without reasons"


class help:
    users = f"\nMentions (@username,{l('Jack Jackson','t.me/username')})"
    until = "\nDate[s|m|h|d|M|y] (1m 30s, 1M)"
    reason = "\n\"Reason\" (Yes in a quote)"

    ban = f"/ban" + users + until + reason
    unban = f"/unban" + users + reason
    kick = f"/kick" + users + reason
    mute = f"/mute" + users + until + reason
    unmute = f"/unmute" + users + reason
