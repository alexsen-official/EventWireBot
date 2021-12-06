from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from commands.back import BACK_COMMAND
from commands.create import CREATE_COMMAND
from commands.delete import DELETE_COMMAND


def events(
    update: Update,
    context: CallbackContext
) -> None:
    send_message(
        update, context,
        EVENTS_COMMAND.description,
        EVENTS_COMMAND.markup
    )


EVENTS_COMMAND = Command(
    callback=events,
    description="🎤 Управление мероприятиями",

    markup=InlineKeyboardMarkup([
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
