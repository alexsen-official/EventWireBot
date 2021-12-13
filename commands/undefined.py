from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.command import Command
from telegram.ext import CallbackContext

from commands.help import HELP_COMMAND
from commands.back import BACK_COMMAND


def undefined(
    update: Update,
    context: CallbackContext
) -> None:
    Bot.send_message(
        update, context,
        UNDEFINED_COMMAND.states["warning"],
        UNDEFINED_COMMAND.markup
    )


UNDEFINED_COMMAND = Command(
    callback=undefined,

    states={
        "warning": (
            "⚠️ <b>Неизвестная команда!</b>\n"
            f"Используйте команду <b>/{HELP_COMMAND.name}</b> для просмотра доступных команд!"
        )
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ]),

    hidden=True
)
