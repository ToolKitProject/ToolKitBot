from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes.Buttons import Button, Menu, Submenu
from libs.classes.Settings import Property, Elements, Settings
from libs.locales import Text as _
from libs import system


class chat:
    class admin:
        undo = Button(_("↩ Undo"), "undo")

        check_poll = Button(_("✅ Check poll"), "check_poll")
        cancel_poll = Button(_("⛔ Cancel poll"), "cancel_poll")

        poll = IM(row_width=1).add(
            check_poll,
            cancel_poll
        )


class private:
    class settings:
        chat_settings = Button(_("Chats"), "chat_settings")
        private_settings = Button(_("Self"), "private_settings")
        settings = Menu(_("Choose what you want to customize"), row_width=2).add(
            chat_settings,
            private_settings
        )

        chat_list = Menu(_("Choose chat"), undo=True)

        class chat:
            add_alias = Button(_("Add alias"), "add_alias")

            settings = Settings(_("Choose what you want to customize"), row_width=2, undo=True).add(
                Property(_("Alias for sticker") + "\n" + _("Click to delete"), _("Alias for sticker"),
                         "sticker_alias", row_width=1).add(
                    add_alias,
                    Elements("{v}", "delete_alias:{k}")
                ),
                Property(_("Alias for text") + "\n" + _("Click to delete"), _("Alias for text"),
                         "text_alias", row_width=1).add(
                    add_alias,
                    Elements("{k} → {v}", "delete_alias:{k}")
                )
            )

            delete = Menu(_("Delete ?"))
            delete_yes = Button(_("Yes 🗑"), "delete_yes")
            delete_no = Button(_("No ↩"), "back")
            delete.add(
                delete_yes,
                delete_no
            )

        class private:
            change_lang = Submenu(_("Choose language"), _("Change language"), "change_lang", row_width=4).add(
                *[Button(t, f"change_lang:{d}")
                  for d, t in system.langs.items()],
                Button("🇬🇧 English", "change_lang:other")
            )

            settings = Settings(_("Choose what you want to customize"), undo=True).add(
                change_lang
            )
        # class chat:
        #     add_alias = Button(_("Add alias"), "add_sticker_alias")

        #     chat_settings = Settings(_("Choose what you want to customize"), "chat_settings").add(
        #         Property(_("Click to delete"), _("Alias for sticker"), "sticker_alias").add(
        #             add_alias,
        #             Elements("{value}", "alias:{key}")
        #         ),
        #         Property(_("Click to delete"), _("Alias for text"), "text_alias").add(
        #             add_alias,
        #             Elements("{key} ➡ {value}", "alias:{key}")
        #         )
        #     )

        #     chats = Menu(_("Choose chat"), undo=True)

        #     delete = Menu(_("Delete ?"))
        #     delete_yes = Button(_("Yes 🗑"), "delete_yes")
        #     delete_no = Button(_("No ↩"), "back")
        #     delete.add(
        #         delete_yes,
        #         delete_no
        #     )

        # class private:
        #     change_lang = Button(_("Change language"), "change_lang")

        # # private_settings = Settings(_("Choose what you want to customize"), _("Self"), "private_settings")

        # chat_settings = Button(_("Chats"), "chat_list")
        # # private_settings = Button(
        # #     private.private_settings.text, private.private_settings.key)
        # settings = Menu(_("Choose what you want to customize"), row_width=2).add(
        #     # private_settings,
        #     chat_settings
        # )


back = Button(_("↩ Back"), "back")
delete_this = Button(_("🗑 Delete"), "delete_this")
