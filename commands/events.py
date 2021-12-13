from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.command import Command
from telegram.ext import CallbackContext

from commands.show import SHOW_COMMAND
from commands.back import BACK_COMMAND
from commands.create import CREATE_COMMAND
from commands.delete import DELETE_COMMAND


def events(
    update: Update,
    context: CallbackContext
) -> None:
    Bot.send_message(
        update, context,
        EVENTS_COMMAND.description,
        EVENTS_COMMAND.markup
    )


EVENTS_COMMAND = Command(
    callback=events,
    description="🎤 Управление мероприятиями\n",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=SHOW_COMMAND.description,
            callback_data=SHOW_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=CREATE_COMMAND.description,
            callback_data=CREATE_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=DELETE_COMMAND.description,
            callback_data=DELETE_COMMAND.name
        )],

        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
