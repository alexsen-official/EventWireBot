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

from config import CHANNELS_FILE
from commands.back import BACK_COMMAND


def attach(
    update: Update,
    context: CallbackContext
) -> int:
    message = update.message

    if message and not Command.filter(message):
        urls = list(message.parse_entities("url").values())

        if urls:
            title = ""

            for last, url in Bot.signal_last(urls):
                chat = Bot.get_chat(context, url)

                if chat is None:
                    state = "error"
                else:
                    channel = {"id": chat.id}
                    title = chat.title

                    if Pyson.find_object(CHANNELS_FILE, chat.id) is not None:
                        state = "warning"
                    else:
                        state = "success"
                        Pyson.append_json(CHANNELS_FILE, channel)

                Bot.send_message(
                    update, context,
                    ATTACH_COMMAND.states[state].format(title),
                    ATTACH_COMMAND.markup if last else None
                )

            return ConversationHandler.END
        else:
            Bot.send_message(
                update, context,
                ATTACH_COMMAND.states["error"]
            )

    Bot.send_message(
        update, context,
        ATTACH_COMMAND.states["default"]
    )

    return ATTACH_COMMAND.id


ATTACH_COMMAND = Command(
    callback=attach,
    description="➕ Привязать канал",

    states={
        "default": "📢 Введите ссылку на канал, который вы хотите привязать к боту: <i>(Перед этим назначьте бота администратором канала)</i>",
        "success": "✅ <b>Канал «‎{}» успешно привязан к боту!</b>",
        "warning": "⚠️ <b>Канал «‎{}» уже привязан к боту!</b>",
        "error": "❌ <b>Ссылка на канал отсутствует или введена неверно!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
