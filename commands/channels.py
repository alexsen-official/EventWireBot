from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.command import Command
from telegram.ext import CallbackContext

from commands.back import BACK_COMMAND
from commands.attach import ATTACH_COMMAND
from commands.detach import DETACH_COMMAND


def channels(
    update: Update,
    context: CallbackContext
) -> None:
    Bot.send_message(
        update, context,
        CHANNELS_COMMAND.description,
        CHANNELS_COMMAND.markup
    )


CHANNELS_COMMAND = Command(
    callback=channels,
    description="📢 Управление каналами\n",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=ATTACH_COMMAND.description,
            callback_data=ATTACH_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=DETACH_COMMAND.description,
            callback_data=DETACH_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
