from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from config import ADMINS_FILE
from commands.back import BACK_COMMAND


def revoke(
    update: Update,
    context: CallbackContext,
    username: str = ""
) -> None:
    keyboard = []

    if not username:
        for admin in Pyson.read_json(ADMINS_FILE):
            username = admin["username"]

            keyboard.append([
                InlineKeyboardButton(
                    text=f"@{username}",
                    callback_data=f"{REVOKE_COMMAND.name} {username}"
                )
            ])

        if keyboard:
            state = "default"
        else:
            state = "warning"
    else:
        if Bot.from_whom(update).username == username:
            state = "error"
        else:
            state = "success"
            Pyson.erase_json(ADMINS_FILE, username)

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    Bot.send_message(
        update, context,
        REVOKE_COMMAND.states[state].format(username),
        InlineKeyboardMarkup(keyboard)
    )


REVOKE_COMMAND = Command(
    callback=revoke,
    description="➖ Разжаловать администратора",

    states={
        "default": "❓ Какого администратора вы хотите разжаловать?",
        "success": "✅ <b>Администратор @{} успешно разжалован!</b>",
        "warning": "⚠️ <b>Нет назначенных администраторов!</b>",
        "error": "❌ <b>Нельзя разжаловать самого себя!</b>"
    }
)
