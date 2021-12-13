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

from commands.help import HELP_COMMAND
from commands.events import EVENTS_COMMAND
from commands.admins import ADMINS_COMMAND
from commands.channels import CHANNELS_COMMAND


def start(
    update: Update,
    context: CallbackContext
) -> int:
    if "state" in context.user_data.keys():
        del context.user_data["state"]

    Bot.send_message(
        update, context,
        START_COMMAND.description,
        START_COMMAND.markup
    )

    return ConversationHandler.END


START_COMMAND = Command(
    callback=start,
    description="🏠 Стартовое меню",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=EVENTS_COMMAND.description,
            callback_data=EVENTS_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=CHANNELS_COMMAND.description,
            callback_data=CHANNELS_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=ADMINS_COMMAND.description,
            callback_data=ADMINS_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=HELP_COMMAND.description,
            callback_data=HELP_COMMAND.name
        )]
    ])
)
