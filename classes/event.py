from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from classes.bot import Bot
from classes.pyson import Pyson
from telegram.ext import CallbackContext

from os import remove
from os.path import exists

from config import (
    EVENTS_FILE,
    CHANNELS_FILE,
    THUMBNAILS_FORMAT,
    THUMBNAILS_DIRECTORY
)

from typing import Any
from sys import maxsize


class Event:
    def generate_id() -> int:
        for id in range(1, maxsize):
            if Pyson.find_object(EVENTS_FILE, id) is None:
                return id

    def photo_path(
        id: int
    ) -> str:
        return f"{THUMBNAILS_DIRECTORY}{id}.{THUMBNAILS_FORMAT}"

    def download_photo(
        update: Update,
        context: CallbackContext
    ) -> bool:
        bot = context.bot
        message = update.message

        Pyson.make_dirs(THUMBNAILS_DIRECTORY)

        try:
            event_id = context.user_data["id"]
            file_id = message.photo[-1].file_id

            path = Event.photo_path(event_id)
            file = bot.get_file(file_id)

            file.download(path)
        except:
            return False

        return True

    def delete_photo(
        id: int
    ) -> None:
        path = Event.photo_path(id)

        if exists(path):
            remove(path)

    def format(
        event: dict[str, Any]
    ) -> dict[str, Any]:
        id = event["id"]

        formatted = {
            "photo_path": Event.photo_path(id),

            "text": (
                f"<b>{event['title']}</b>\n\n"
                f"📅 <b>Дата:</b> {event['date']}\n"
                f"🕘 <b>Время:</b> {event['time']}\n"
                f"🌍 <b>Место:</b> {event['place']}\n\n"
                f"{event['description']}\n\n"
            ),

            "markup": InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="👍 0",
                    callback_data=f"{Event.like.__name__} {id}"
                ),

                InlineKeyboardButton(
                    text="👎 0",
                    callback_data=f"{Event.dislike.__name__} {id}"
                )],

                [InlineKeyboardButton(
                    text="👁️ Подробнее",
                    url=event["url"]
                )]
            ])
        }

        return formatted

    def save(
        update: Update,
        context: CallbackContext
    ) -> int:
        event = {
            "id": context.user_data["id"],
            "title": context.user_data["title"],
            "date": context.user_data["date"],
            "time": context.user_data["time"],
            "place": context.user_data["place"],
            "description": context.user_data["description"],
            "url": context.user_data["url"],
            "created": Bot.from_whom(update).username,
            "published": [],
            "liked": [],
            "disliked": []
        }

        Pyson.append_json(EVENTS_FILE, event)
        return event["id"]

    def publish(
        update: Update,
        context: CallbackContext,
        id: int
    ) -> None:
        channels = Pyson.read_json(CHANNELS_FILE)
        event = Pyson.find_object(EVENTS_FILE, id)
        formatted = Event.format(event)

        if channels:
            for channel in channels:
                sent = Bot.send_message(
                    update, context,
                    formatted["text"],
                    formatted["markup"],
                    formatted["photo_path"],
                    channel["id"],
                    history_record=False
                )

                event["published"].append(sent.to_dict())

        Pyson.erase_json(EVENTS_FILE, id)
        Pyson.append_json(EVENTS_FILE, event)

    def feedback(
        update: Update,
        context: CallbackContext,
        id: int,
        dislike: bool = False
    ) -> None:
        bot = context.bot
        event = Pyson.find_object(EVENTS_FILE, id)
        user_id = Bot.from_whom(update).id
        reactions = ["liked", "disliked"]

        if dislike:
            reactions.reverse()

        if user_id in event[reactions[0]]:
            event[reactions[0]].remove(user_id)
        else:
            event[reactions[0]].append(user_id)

            if user_id in event[reactions[1]]:
                event[reactions[1]].remove(user_id)

        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text=f"👍 {len(event['liked'])}",
                callback_data=f"{Event.like.__name__} {id}"
            ),

            InlineKeyboardButton(
                text=f"👎 {len(event['disliked'])}",
                callback_data=f"{Event.dislike.__name__} {id}"
            )],

            [InlineKeyboardButton(
                text="👁️ Подробнее",
                url=event["url"]
            )]
        ])

        for publication in event["published"]:
            bot.edit_message_reply_markup(
                publication["chat"]["id"],
                publication["message_id"],
                reply_markup=markup
            )

        Pyson.erase_json(EVENTS_FILE, id)
        Pyson.append_json(EVENTS_FILE, event)

    def like(
        update: Update,
        context: CallbackContext,
        id: int
    ) -> None:
        Event.feedback(update, context, int(id))

    def dislike(
        update: Update,
        context: CallbackContext,
        id: int
    ) -> None:
        Event.feedback(update, context, int(id), dislike=True)
