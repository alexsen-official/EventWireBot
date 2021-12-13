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
    if not HELP_COMMAND.states["default"]:
        for command in Command.commands:
            HELP_COMMAND.states["default"] += f"<b>/{command.name}</b> - {command.description}\n"

    Bot.send_message(
        update, context,
        HELP_COMMAND.states["default"],
        HELP_COMMAND.markup
    )


HELP_COMMAND = Command(
    callback=help,
    description="🔎 Просмотр доступных команд\n",

    states={
        "default": ""
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
