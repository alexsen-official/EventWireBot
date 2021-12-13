from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from classes.bot import Bot
from classes.command import Command

from typing import Any
from commands.back import BACK_COMMAND
from commands.undefined import UNDEFINED_COMMAND


def cancel(
    update: Update,
    context: CallbackContext
) -> Any:
    message = update.message

    Bot.send_message(
        update, context,
        CANCEL_COMMAND.states["warning"],
        CANCEL_COMMAND.markup
    )

    if message and Command.filter(message):
        try:
            return globals()[message[1:]](update, context)
        except:
            return UNDEFINED_COMMAND.callback(update, context)

    return ConversationHandler.END


CANCEL_COMMAND = Command(
    callback=cancel,

    states={
        "warning": "⚠️ <b>Выполнение предыдущей команды было прервано!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ]),

    hidden=True
)
