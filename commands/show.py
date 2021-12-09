from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.event import Event
from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from config import (
    EVENTS_FILE,
    MAX_MESSAGES
)

from commands.back import BACK_COMMAND


def show(
    update: Update,
    context: CallbackContext
) -> None:
    events = Pyson.read_json(EVENTS_FILE)

    if events:
        showed = 0
        Bot.delete_previous_message(update, context)

        for event in events:
            showed += 1
            formatted = Event.format(event)

            if showed > MAX_MESSAGES:
                break

            text = formatted["text"]
            text += f"📢 Количество публикаций: <b>{len(event['published'])}</b>\n"
            text += f"👨🏻‍💻 Создано: <b>@{event['created']}</b>"

            Bot.send_message(
                update, context, text,
                formatted["markup"],
                formatted["photo_path"]
            )

        response = SHOW_COMMAND.states["success"].format(
            showed if showed > 1 else ""
        )

        Bot.send_message(
            update, context, response,
            SHOW_COMMAND.markup
        )
    else:
        Bot.edit_previous_message(
            update, context,
            SHOW_COMMAND.states["warning"],
            SHOW_COMMAND.markup
        )


SHOW_COMMAND = Command(
    callback=show,
    description="📑 Список мероприятий",

    states={
        "warning": "⚠️ <b>Нет опубликованных мероприятий!</b>",
        "success": "✅ <b>Успешно показана информация о {} последних меропритиях!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
