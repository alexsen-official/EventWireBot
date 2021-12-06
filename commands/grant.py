from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from classes.pyson import Pyson
from classes.command import Command

from classes.bot import (
    signal_last,
    send_message,
    delete_messages
)

from config import ADMINS_FILE
from commands.back import BACK_COMMAND


def grant(
    update: Update,
    context: CallbackContext
) -> str:
    message = update.message
    blank = True

    if message and not Command.filter(message):
        mentions = list(message.parse_entities("mention").values())
        delete_messages(update, context)

        if mentions:
            admins = Pyson.read(ADMINS_FILE)
            markup = None

            for last, mention in signal_last(mentions):
                username = str(mention)[1:]
                admin = {"username": username}

                if admin in admins:
                    state = "warning"
                else:
                    Pyson.append(ADMINS_FILE, admin)
                    state = "success"

                if last:
                    markup = GRANT_COMMAND.markup

                response = GRANT_COMMAND.states[state].format(username)
                send_message(update, context, response, markup, blank=False)

            return ConversationHandler.END
        else:
            blank = False
            send_message(update, context, GRANT_COMMAND.states["error"])

    send_message(
        update, context,
        GRANT_COMMAND.states["default"],
        GRANT_COMMAND.markup, blank=blank
    )

    return GRANT_COMMAND.name


GRANT_COMMAND = Command(
    callback=grant,
    description="➕ Назначить администратора",

    states={
        "default": "👨🏻‍💻 Введите имя пользователя, которого вы хотите назначить администратором: ",
        "success": "✅ <b>Пользователь @{} успешно назначен администратором!</b>",
        "warning": "⚠️ <b>Пользователь @{} уже является администратором!</b>",
        "error": "❌ <b>Имя пользователя отсутствует или введено неверно!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
