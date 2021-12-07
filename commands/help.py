from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.command import Command
from telegram.ext import CallbackContext

from commands.back import BACK_COMMAND


def help(
    update: Update,
    context: CallbackContext
) -> None:
    response = ""

    for command in Command.commands:
        response += f"<b>/{command.name}</b> - {command.description}\n"

    Bot.edit_previous_message(
        update, context, response,
        HELP_COMMAND.markup
    )


HELP_COMMAND = Command(
    callback=help,
    description="🔎 Просмотр доступных команд\n",

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
