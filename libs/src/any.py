from libs.classes import CommandParser as p
from libs.classes import Commands as c
from libs.system import regex as r
from libs.system import restrict_commands
from aiogram.utils.markdown import hlink as l
from libs.locales import Text as _


class commands:
    class _help_text:
        users = _(
            "👥 Mentions (@username,<a href=\"t.me/username\">Jack Jackson</a> or reply)")
        until = _("⏳ Date[s|m|h|d|M|y] (1m 30s or 1M)")
        reason = _("❔ \"Reason\" (Yes in the quote)")
        poll = _("📈 Make a poll (-p --poll)")

        ban = [users, until, reason, poll]
        unban = [users, reason, poll]
        kick = [users, reason, poll]
        mute = [users, until, reason, poll]
        unmute = [users, reason, poll]

        count = _("🔢 Count (2 - 1000)")
        reply = _("⤴ Reply to delete above")

        purge = [count, reply]

    hide = c.Hide().add(
        c.Command("cancel", _("◀️ To cancel"),
                  _("Exit from form"))
    )

    default_commands = c.Default().add(
        c.Command("fix", _("🔧 Fix hints for commands"),
                  _("Fixes hints for commands")),
        c.Command("help", _("🚑 Help for commands"),
                  _("Shows help (/help or /help ban)"))
    )

    private_commands = c.Private().add(
        c.Command("settings", _("⚙ Settings"), _("Shows settings"))
    )

    chat_commands = c.AllChat().add(

    )

    chat_admin_commands = c.AllAdmins().add(
        c.Command("ban", _("⛔ Block user"), *_help_text.ban),
        c.Command("unban", _("✅ Unblock user"), *_help_text.unban),
        c.Command("kick", _("⚠ Kick user"), *_help_text.kick),
        c.Command("mute", _("🔇 Mute user"), *_help_text.mute),
        c.Command("unmute", _("🔈 Unmute user"), *_help_text.unmute),
        c.Command("purge", _("🗑 Purge messages"), *_help_text.purge),
    )


class parsers:
    help = p.Command("help", _("Help command")).add(
        p.TextArg(_("Command"), "cmd", sep="")
    )

    restrict = p.Command(restrict_commands, _("Admin command")).add(
        p.Arg(r.parse.reason, "reason", _("Reason"), False),
        p.DateArg(_("Date")),
        p.UserArg(_("User")),
        p.FlagArg().add(
            p.Flag("p", "poll", "poll", "Poll flag")
        )
    )

    purge = p.Command("purge", _("Purge command")).add(
        p.NumberArg(2, 1000, _("Message count"), required=True)
    )


command_list = c.Commands("other").add(
    commands.hide,
    commands.default_commands,
    commands.private_commands,
    commands.chat_commands,
    commands.chat_admin_commands
)
