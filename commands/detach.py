from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from config import CHANNELS_FILE
from commands.back import BACK_COMMAND


def detach(
    update: Update,
    context: CallbackContext,
    id: int = None
) -> None:
    title = ""
    keyboard = []
    bot = context.bot

    if id is None:
        for channel in Pyson.read_json(CHANNELS_FILE):
            channel = bot.get_chat(channel["id"])

            keyboard.append([
                InlineKeyboardButton(
                    text=channel.title,
                    callback_data=f"{DETACH_COMMAND.name} {channel.id}"
                )
            ])

        if keyboard:
            state = "default"
        else:
            state = "warning"
    else:
        state = "success"
        channel = bot.get_chat(id)
        title = channel.title

        channel.leave()
        Pyson.erase_json(CHANNELS_FILE, channel.id)

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    Bot.edit_previous_message(
        update, context,
        DETACH_COMMAND.states[state].format(title),
        InlineKeyboardMarkup(keyboard)
    )


DETACH_COMMAND = Command(
    callback=detach,
    description="➖ Отвязать канал",

    states={
        "default": "❓ Какой канал вы хотите отвязать от бота?",
        "success": "✅ <b>Канал «{}» успешно отвязан от бота!</b>",
        "warning": "⚠️ <b>Нет привязанных к боту каналов!</b>"
    }
)
