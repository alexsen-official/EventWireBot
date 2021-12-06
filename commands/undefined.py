from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from commands.back import BACK_COMMAND


def undefined(
    update: Update,
    context: CallbackContext
) -> None:
    send_message(
        update, context,
        UNDEFINED_COMMAND.description,
        UNDEFINED_COMMAND.markup
    )


UNDEFINED_COMMAND = Command(
    callback=undefined,
    description="⚠️ Неизвестная команда!",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ]),

    hidden=True
)
