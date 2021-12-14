from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.event import Event
from classes.pyson import Pyson
from classes.command import Command
from telegram.message import Message
from telegram.ext import CallbackContext

from config import EVENTS_FILE
from commands.back import BACK_COMMAND


def delete(
    update: Update,
    context: CallbackContext,
    id: int = None
) -> None:
    title = ""
    keyboard = []
    bot = context.bot

    if id is None:
        for event in Pyson.read_json(EVENTS_FILE):
            keyboard.append([
                InlineKeyboardButton(
                    text=event["title"],
                    callback_data=f"{DELETE_COMMAND.name} {event['id']}"
                )
            ])

        if keyboard:
            state = "default"
        else:
            state = "warning"
    else:
        id = int(id)
        state = "success"
        event = Pyson.find_object(EVENTS_FILE, id)
        title = event["title"]

        for message in event["messages"]:
            Bot.delete_message(update, context, Message.de_json(message, bot))

        Event.delete_photo(id)
        Pyson.erase_json(EVENTS_FILE, id)

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    Bot.send_message(
        update, context,
        DELETE_COMMAND.states[state].format(title),
        InlineKeyboardMarkup(keyboard)
    )


DELETE_COMMAND = Command(
    callback=delete,
    description="➖ Удалить мероприятие",

    states={
        "default": "❓ Какое мероприятие вы хотите удалить?",
        "success": "✅ <b>Мероприятие «{}» успешно удалено!</b>",
        "warning": "⚠️ <b>Нет опубликованных мероприятий!</b>"
    }
)
