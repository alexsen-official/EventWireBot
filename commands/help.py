from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from commands.back import BACK_COMMAND


def help(
    update: Update,
    context: CallbackContext
) -> None:
    response = ""

    for command in Command.commands:
        response += f"<b>/{command.name}</b> - {command.description}\n"

    send_message(update, context, response, HELP_COMMAND.markup)


HELP_COMMAND = Command(
    callback=help,
    description="🔎 Просмотр доступных команд",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
