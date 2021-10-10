from datetime import timedelta

import src.parsers as p
from libs import commands as c
from libs.locales import Text as _
from locales import text
from src.commands import restrict_commands


def _poll_expire(value: str):
    num = float(value)

    if num < 1:
        raise RuntimeError()
    if num > 10:
        raise RuntimeError()

    return num * 60


class commands:
    class _help_text:
        users = _(
            "👥 Mentions (@username,<a href=\"t.me/username\">Jack Jackson</a> or reply)")
        until = _("⏳ Date[s|m|h|d|M|y] (1m 30s or 1M)")
        reason = _("❔ \"Reason\" (Yes in the quote)")
        poll = _(
            "📈 Make a poll (-p --poll) \n"
            "🎭 Make poll anonymous (-a --anonym) \n"
            "⌚ Set poll expire time (-e=600 --expire:65) (1 - 10 min)"
        )
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
    report_count = p.TextParser().add(
        p.NumberArg(
            _("Report count"),
            dest="count",
            minimal=3,
            maximal=20,
            required=True
        )
    )
    report_delta = p.TextParser().add(
        p.DateArg(
            _("Report delta"),
            dest="delta",
            minimum=timedelta(days=1),
            maximum=timedelta(days=366),
            required=True
        )
    )

    test = p.CommandParser("test", "Test command").add(
        p.DateArg(_("Date"), dest="delta", default=timedelta(minutes=1))
    )

    help = p.CommandParser("help", _("Help command")).add(
        p.TextArg(_("Command"), "cmd", sep="")
    )

    restrict = p.CommandParser(restrict_commands, _("Admin command")).add(
        p.ReasonArg(_("Reason"), default=text.chat.admin.reason_empty),
        p.DateArg(_("Date"), dest="until"),
        p.UserArg(_("User"), dest="targets"),
        p.FlagArg().add(
            p.Flag("p", "poll", dest="poll", name=_("Poll flag")),
            p.Flag("a", "anonym_poll",
                   dest="anonym",
                   name=_("Anonym poll flag")),
            p.Flag("c", "clear-history",
                   dest="clear_history",
                   name=_("Clear history flag")),
            p.ValueFlag("e", "expire",
                        dest="poll_delta",
                        name=_("Poll expire flag"),
                        default=None,
                        func=_poll_expire)
        )
    )

    report = p.CommandParser("report", _("Report codrcmmand")).add(
        p.ReasonArg(_("Reason"), default=text.chat.admin.reason_empty),
        p.UserArg(_("User"), dest="targets")
    )

    clear_history = p.CommandParser("clear_history", _("Clear history command")).add(
        p.UserArg(_("User"), dest="targets"),
        p.DateArg(_("Date"), dest="time", default=timedelta(days=1))
    )

    purge = p.CommandParser("purge", _("Purge command")).add(
        p.NumberArg(_("Message count"), 2, 1000, dest="count", required=True)
    )


command_list = c.Commands().add(
    commands.hide,
    commands.default_commands,
    commands.private_commands,
    commands.chat_commands,
    commands.chat_admin_commands
)
