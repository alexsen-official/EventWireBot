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
    show_message = Bot.edit_previous_message

    if len(events) > 10:
        events = events[:-10]

    if events:
        first = True

        for last, event in Bot.signal_last(events):
            formatted = Event.format(event)

            text = formatted["text"]
            text += f"👨🏻‍💻 Создано: <b>@{event['created']}</b>"

            markup = formatted["markup"]

            if first:
                first = False
            else:
                show_message = Bot.send_message

            if last:
                markup.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=BACK_COMMAND.description,
                        callback_data=BACK_COMMAND.name
                    )
                ])

            show_message(update, context, text, markup)
    else:
        show_message(
            update, context,
            SHOW_COMMAND.states["warning"],
            SHOW_COMMAND.markup
        )


SHOW_COMMAND = Command(
    callback=show,
    description="📑 Список мероприятий",

    states={
        "warning": "⚠️ <b>Нет опубликованных мероприятий!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
