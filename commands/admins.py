from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from commands.back import BACK_COMMAND
from commands.grant import GRANT_COMMAND
from commands.revoke import REVOKE_COMMAND


def admins(
    update: Update,
    context: CallbackContext
) -> None:
    send_message(
        update, context,
        ADMINS_COMMAND.description,
        ADMINS_COMMAND.markup
    )


ADMINS_COMMAND = Command(
    callback=admins,
    description="👨🏻‍💻 Управление администраторами",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=GRANT_COMMAND.description,
            callback_data=GRANT_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=REVOKE_COMMAND.description,
            callback_data=REVOKE_COMMAND.name
        )],


        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
