from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import send_message

from config import ADMINS_FILE
from commands.back import BACK_COMMAND


def revoke(
    update: Update,
    context: CallbackContext,
    username: str = None
) -> None:
    query = update.callback_query
    state = "default"
    keyboard = []

    if username is None:
        for admin in Pyson.read(ADMINS_FILE):
            keyboard.append([
                InlineKeyboardButton(
                    text=admin["username"],
                    callback_data=f"{REVOKE_COMMAND.name} {admin['username']}"
                )
            ])

        if not keyboard:
            state = "warning"
    else:
        if query.from_user.username == username:
            state = "error"
        else:
            Pyson.erase(ADMINS_FILE, username=username)
            state = "success"

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    response = REVOKE_COMMAND.states[state].format(username)
    send_message(update, context, response, InlineKeyboardMarkup(keyboard))


REVOKE_COMMAND = Command(
    callback=revoke,
    description="➖ Разжаловать администратора",

    states={
        "default": "❓ <b>Какого администратора вы хотите разжаловать?</b>",
        "success": "✅ <b>Администратор @{} успешно разжалован!</b>",
        "warning": "⚠️ <b>Нет назначенных администраторов!</b>",
        "error": "❌ <b>Нельзя разжаловать самого себя!</b>"
    }
)
