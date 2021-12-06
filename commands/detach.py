from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from config import CHANNELS_FILE
from commands.back import BACK_COMMAND


def detach(
    update: Update,
    context: CallbackContext,
    id: int = None
) -> None:
    bot = context.bot
    state = "default"
    keyboard = []
    title = ""

    if id is None:
        for channel in Pyson.read(CHANNELS_FILE):
            keyboard.append([
                InlineKeyboardButton(
                    text=bot.get_chat(channel["id"]).title,
                    callback_data=f"{DETACH_COMMAND.name} {channel['id']}"
                )
            ])

        if not keyboard:
            state = "warning"
    else:
        Pyson.erase(CHANNELS_FILE, id=int(id))

        title = bot.get_chat(id).title
        state = "success"

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    response = DETACH_COMMAND.states[state].format(title)
    send_message(update, context, response, InlineKeyboardMarkup(keyboard))


DETACH_COMMAND = Command(
    callback=detach,
    description="➖ Отвязать канал",

    states={
        "default": "❓ <b>Какой канал вы хотите отвязать?</b>",
        "success": "✅ <b>Канал «{}» успешно отвязан от бота!</b>",
        "warning": "⚠️ <b>Нет связанных каналов!</b>"
    }
)
