from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.pyson import Pyson
from classes.command import Command
from telegram.ext import CallbackContext

from classes.bot import (
    send_message,
    delete_message
)

from os import remove
from os.path import exists

from config import (
    EVENTS_FILE,
    THUMBNAILS_DIRECTORY
)

from commands.back import BACK_COMMAND


def delete(
    update: Update,
    context: CallbackContext,
    id: int = None
) -> None:
    state = "default"
    keyboard = []
    title = ""

    if id is None:
        for event in Pyson.read(EVENTS_FILE):
            keyboard.append([
                InlineKeyboardButton(
                    text=event["title"],
                    callback_data=f"{DELETE_COMMAND.name} {event['id']}"
                )
            ])

        if not keyboard:
            state = "warning"
    else:
        for event in Pyson.read(EVENTS_FILE):
            if event["id"] == int(id):
                for publication in event["published"]:
                    thumbnail = f"{THUMBNAILS_DIRECTORY}/{event['id']}.jpg"

                    delete_message(
                        update, context,
                        publication["message_id"],
                        publication["chat_id"]
                    )

                    if exists(thumbnail):
                        remove(thumbnail)

                title = event["title"]
                break

        Pyson.erase(EVENTS_FILE, id=int(id))
        state = "success"

    keyboard.append([
        InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )
    ])

    response = DELETE_COMMAND.states[state].format(title)
    send_message(update, context, response, InlineKeyboardMarkup(keyboard))


DELETE_COMMAND = Command(
    callback=delete,
    description="➖ Удалить мероприятие",

    states={
        "default": "❓ <b>Какое мероприятие вы хотите удалить?</b>",
        "success": "✅ <b>Мероприятие «{}» успешно удалено!</b>",
        "warning": "⚠️ <b>Нет опубликованных мероприятий!</b>"
    }
)
