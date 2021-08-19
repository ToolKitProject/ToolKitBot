from click import command
from libs.locales import Text as _

cancel = _("/cancel - to cancel")

statistic_modes = {
    0: _("Off"),
    1: _("Date only"),
    2: _("Full")
}


class errors:
    class restrict:
        pass

    class argument_error:
        ArgumentError = _("⚠ Invalid argument")

        incorrect = _("Argument <b>{arg_name}</b> incorrect")
        required = _("Argument <b>{arg_name}</b> required")

    class alias_type_error:
        AliasTypeError = _("⚠ Wrong type")

        command_not_supported = _("Command not supported")
        sticker_supported = _("Only sticker supported")
        text_supported = _("Only text supported")

    CommandNotFound = _("⚠ Command not found")
    UserNotFound = _("⚠ User not found")
    HasNotPermission = _("⚠ You don't have the permission")
    EmptyOwns = _("⚠ You do not own chats")
    AlreadyExists = _("⚠ Already exists")
    NotReply = _("⚠ Not replied")
    BotHasNotPermission = _("⚠ The bot has no or not enough rights")
    BackError = _("⚠ Back error")
    PollCheck = _("⚠ Not enough votes")


class private:
    start_text = _("Hi, I am a ToolKit bot and I am dedicated to everything you can imagine 😜 \n" +
                   "What I can do 😊 \n" +
                   "┣ Edit photo 🌅 \n" +
                   "┣ Moderate groups ⚙️ \n" +
                   "┣ Decrypt voice 🎤 \n" +
                   "┣ Generate voice 🎙 \n" +
                   "┗ Generate memes 😎")

    class settings:
        chat_loading = _("🕒 Please wait,chats is loading")
        sticker = _("1⃣ Send me sticker \n") + cancel
        text = _("1⃣ Send me text \n") + cancel

        command = _("2⃣ Send me command")

        statistic_mode_changed = _("Statistic mode changed on {mode}")


class chat:
    _perm = _("┣ /ban /unban ⛔ \n" +
              "┣ /mute /unmute 🔇 \n" +
              "┣ /purge 🗑 \n" +
              "┗ /kick ⚠")

    start_text = _("Hello i am ToolKit bot \n" +
                   "What i can do this chat \n" +
                   "┣ Moderate ⚙️ \n" +
                   "┗ Decrypt voice messages 🎤 \n" +
                   " \n" +
                   "For administration commands to work, please grant these rights \n" +
                   "┣ Delete messages ⚠ \n" +
                   "┣ Invite links 🔗 \n" +
                   "┗ Ban user ⛔")
    promote_admin = _("The bot now <b>has</b> administrator rights \n" +
                      "Now you <b>can</b> use commands like \n"
                      ) + _perm
    restrict_admin = _("The bot now <b>hasn't</b> administrator rights \n" +
                       "Now you <b>can't</b> use commands like \n"
                       ) + _perm

    fix_commands = _("✅ Commands fixed")

    class admin:
        reason = _("Reason ❓ - <code>{reason}</code> \n")
        admin = _("Moderator 👤 - <i>{admin}</i> \n")
        until = _("Until ⌛ - <b>{until}</b> \n")

        unmute = _("User {user} unmuted 🔈 \n") + reason + admin
        multi_unmute = _("Users {user} unmuted 🔈 \n") + reason + admin
        unmute_poll = _("🔈 Unmute - {user} ?")

        mute = _("User {user} muted 🔇 \n") + reason + admin + until
        multi_mute = _("Users {user} muted 🔇 \n") + reason + admin + until
        mute_poll = _("🔇 Mute - {user} ?")

        kick = _("User {user} kicked out ⚠ \n") + reason + admin
        multi_kick = _("Users {user} kicked out ⚠ \n") + reason + admin
        kick_poll = _("⚠ Kick out - {user} ?")

        unban = _("User {user} unbanned ✅ \n") + reason + admin
        multi_unban = _("Users {user} unbanned ✅ \n") + reason + admin
        unban_poll = _("✅ Unban - {user} ?")

        ban = _("User {user} banned ⛔ \n") + reason + admin + until
        multi_ban = _("Users {user} banned ⛔ \n") + reason + admin + until
        ban_poll = _("⛔ Ban - {user} ?")

        options_poll = [_("✅ Yes"), _("⛔ No ")]

        forever = _("February 31, 1970")
        reason_empty = _("Without any reasons")

        purge = _("🗑 Chat purged of {count} messages")
