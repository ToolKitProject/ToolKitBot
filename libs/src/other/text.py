from aiogram.utils.markdown import hlink as l


class errors:
    until = "If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever."

    CommandNotFound = "⚠ Command not found"
    UserNotFound = "⚠ User not found"
    ArgumentError = "⚠ Invalid argument"
    HasNotPermission = "⚠ You has not permission"
    UntilWaring = f"❗ {until}"


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
    reason = "\n(Reason) (Text from 3 characters)"

    ban = f"/ban" + users + until + reason
    unban = f"/unban" + users + reason
    kick = f"/kick" + users + reason
    mute = f"/mute" + users + until + reason
    unmute = f"/unmute" + users + reason
