from datetime import timedelta

import src.parsers as p
from libs import commands as c
from libs.locales import Text as _
from locales import text
from src.system import restrict_commands


class commands:
    class _help_text:
        users = _(
            "👥 Mentions (@username,<a href=\"t.me/username\">Jack Jackson</a> or reply)")
        until = _("⏳ Date[s|m|h|d|M|y] (1m 30s or 1M)")
        reason = _("❔ \"Reason\" (Yes in the quote)")
        poll = _("📈 Make a poll (-p --poll)")
        clear_history_flag = _(
            "🔥 Delete messages sent by the user") + "(-c --clear-history)"
        count = _("🔢 Count (2 - 1000)")
        reply = _("⤴ Reply to delete above")

        ban = [users, until, reason, poll, clear_history_flag]
        unban = [users, reason, poll]
        kick = [users, reason, poll, clear_history_flag]
        mute = [users, until, reason, poll, clear_history_flag]
        unmute = [users, reason, poll]
        purge = [count, reply]
        clear_history = [users, until]
        report = [users, reason]

    hide = c.Hide().add(
        c.Command("cancel", _("◀ To cancel"),
                  _("Exit from form"))
    )

    default_commands = c.Default().add(
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
        c.Command("clear_history", _(
            "🔥 Delete messages sent by the user"), *_help_text.clear_history),
        c.Command("report", _("‼️ Report user"), *_help_text.report)
    )


class parsers:
    test = p.Command("test", "Test command").add(
        p.DateArg(_("Date"), dest="delta", default=timedelta(minutes=1))
    )

    help = p.Command("help", _("Help command")).add(
        p.TextArg(_("Command"), "cmd", sep="")
    )

    restrict = p.Command(restrict_commands, _("Admin command")).add(
        p.ReasonArg(_("Reason"), default=text.chat.admin.reason_empty),
        p.DateArg(_("Date"), dest="until", default=None),
        p.UserArg(_("User"), dest="targets"),
        p.FlagArg().add(
            p.Flag("p", "poll", dest="poll", name=_("Poll flag")),
            p.Flag("c", "clear-history", dest="clear_history",
                   name=_("Clear history flag"))
        )
    )

    report = p.Command("report", _("Report command")).add(
        p.ReasonArg(_("Reason"), default=text.chat.admin.reason_empty),
        p.UserArg(_("User"), dest="targets")
    )

    clear_history = p.Command("clear_history", _("Clear history command")).add(
        p.UserArg(_("User"), dest="target"),
        p.DateArg(_("Date"), dest="time", default=timedelta(days=1))
    )

    purge = p.Command("purge", _("Purge command")).add(
        p.NumberArg(_("Message count"), 2, 1000, dest="count", required=True)
    )


command_list = c.Commands().add(
    commands.hide,
    commands.default_commands,
    commands.private_commands,
    commands.chat_commands,
    commands.chat_admin_commands
)
