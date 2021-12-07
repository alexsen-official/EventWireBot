from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.command import Command
from telegram.ext import CallbackContext

from commands.back import BACK_COMMAND
from commands.grant import GRANT_COMMAND
from commands.revoke import REVOKE_COMMAND


def admins(
    update: Update,
    context: CallbackContext
) -> None:
    Bot.edit_previous_message(
        update, context,
        ADMINS_COMMAND.description,
        ADMINS_COMMAND.markup
    )


ADMINS_COMMAND = Command(
    callback=admins,
    description="👨🏻‍💻 Управление администраторами\n",

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
