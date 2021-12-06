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
    delete_message,
    delete_messages
)

from json import loads
from urllib.request import urlopen

from config import (
    BOT_TOKEN,
    CHANNELS_FILE
)

from commands.back import BACK_COMMAND


def attach(
    update: Update,
    context: CallbackContext
) -> str:
    message = update.message
    bot = context.bot
    blank = True
    title = ""

    if message and not Command.filter(message):
        urls = list(message.parse_entities("url").values())
        delete_messages(update, context)

        if urls:
            channels = Pyson.read(CHANNELS_FILE)
            domain = ".me/"
            markup = None

            for last, url in signal_last(urls):
                mention = url[url.find(domain) + len(domain):]

                try:
                    with urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?text=!&chat_id=@{mention}") as page:
                        data = loads(page.read().decode())

                        chat_id = data["result"]["chat"]["id"]
                        message_id = data["result"]["message_id"]

                        channel = {"id": chat_id}
                        title = bot.get_chat(chat_id).title

                        delete_message(update, context, message_id, chat_id)

                        if channel in channels:
                            state = "warning"
                        else:
                            Pyson.append(CHANNELS_FILE, channel)
                            state = "success"
                except:
                    state = "error"

                if last:
                    markup = ATTACH_COMMAND.markup

                response = ATTACH_COMMAND.states[state].format(title)
                send_message(update, context, response, markup, blank=False)

            return ConversationHandler.END
        else:
            blank = False
            send_message(update, context, ATTACH_COMMAND.states["error"])

    send_message(
        update, context,
        ATTACH_COMMAND.states["default"],
        ATTACH_COMMAND.markup, blank=blank
    )

    return ATTACH_COMMAND.name


ATTACH_COMMAND = Command(
    callback=attach,
    description="➕ Привязать канал",

    states={
        "default": "📢 Введите ссылку на канал, который вы хотите привязать к боту: ",
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
