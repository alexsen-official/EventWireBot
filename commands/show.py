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

from config import EVENTS_FILE
from commands.back import BACK_COMMAND


def show(
    update: Update,
    context: CallbackContext
) -> None:
    events = Pyson.read_json(EVENTS_FILE)

    if len(events) > 10:
        events = events[-10]

    if events:
        for event in events:
            formatted = Event.format(event)

            text = formatted["text"]
            text += f"📢 Количество публикаций: <b>{len(event['messages'])}</b>\n"
            text += f"👨🏻‍💻 Создано: <b>@{event['admin']}</b>"

            Bot.delete_message(update, context, update.callback_query.message)

            Bot.send_message(
                update, context, text,
                formatted["reply_markup"],
                formatted["photo_path"],
                blank=True
            )

        Bot.send_message(
            update, context,
            SHOW_COMMAND.states["success"],
            SHOW_COMMAND.markup
        )
    else:
        Bot.send_message(
            update, context,
            SHOW_COMMAND.states["warning"],
            SHOW_COMMAND.markup
        )


SHOW_COMMAND = Command(
    callback=show,
    description="📑 Список мероприятий",

    states={
        "warning": "⚠️ <b>Нет опубликованных мероприятий!</b>",
        "success": "✅ <b>Успешно показана информация о последних меропритиях!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
