from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from classes.command import Command

from classes.bot import (
    send_message,
    delete_messages
)

from typing import Any
from commands.back import BACK_COMMAND
from commands.undefined import UNDEFINED_COMMAND


def cancel(
    update: Update,
    context: CallbackContext
) -> Any:
    message = update.message

    delete_messages(update, context)

    if message:
        if Command.filter(message):
            send_message(
                update, context,
                CANCEL_COMMAND.description,
                blank=True
            )

            try:
                return globals()[message[1:]](update, context)
            except:
                return UNDEFINED_COMMAND.callback(update, context)

    send_message(
        update, context,
        CANCEL_COMMAND.description,
        CANCEL_COMMAND.markup
    )

    return ConversationHandler.END


CANCEL_COMMAND = Command(
    callback=cancel,
    description="⚠️ <b>Выполнение предыдущей команды было прервано!</b>",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ]),

    hidden=True
)
