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
from classes.pyson import Pyson
from classes.command import Command

from config import ADMINS_FILE
from commands.back import BACK_COMMAND


def grant(
    update: Update,
    context: CallbackContext
) -> int:
    message = update.message

    if message and not Command.filter(message):
        mentions = list(message.parse_entities("mention").values())

        if mentions:
            for last, mention in Bot.signal_last(mentions):
                username = mention[1:]
                admin = {"username": username}

                if Pyson.find_object(ADMINS_FILE, username) is not None:
                    state = "warning"
                else:
                    state = "success"
                    Pyson.append_json(ADMINS_FILE, admin)

                Bot.send_message(
                    update, context,
                    GRANT_COMMAND.states[state].format(mention),
                    GRANT_COMMAND.markup if last else None
                )

            return ConversationHandler.END
        else:
            Bot.send_message(
                update, context,
                GRANT_COMMAND.states["error"]
            )

    Bot.send_message(
        update, context,
        GRANT_COMMAND.states["default"]
    )

    return GRANT_COMMAND.id


GRANT_COMMAND = Command(
    callback=grant,
    description="➕ Назначить администратора",

    states={
        "default": "👨🏻‍💻 Введите имя пользователя, которого вы хотите назначить администратором: ",
        "success": "✅ <b>Пользователь {} успешно назначен администратором!</b>",
        "warning": "⚠️ <b>Пользователь {} уже является администратором!</b>",
        "error": "❌ <b>Имя пользователя отсутствует или введено неверно!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
