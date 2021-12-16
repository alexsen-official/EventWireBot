from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.message import Message

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
        for event_id in range(1, maxsize):
            if Pyson.find_object(EVENTS_FILE, event_id) is None:
                return event_id

    def photo_path(
        event_id: int
    ) -> str:
        return f"{THUMBNAILS_DIRECTORY}{event_id}.{THUMBNAILS_FORMAT}"

    def download_photo(
        update: Update,
        context: CallbackContext
    ) -> bool:
        bot = context.bot
        message = update.message

        Pyson.make_dirs(THUMBNAILS_DIRECTORY)

        try:
            event_id = context.user_data["id"]
            photo_id = message.photo[-1].file_id

            photo_path = Event.photo_path(event_id)
            photo = bot.get_file(photo_id)

            photo.download(photo_path)
        except:
            return False

        return True

    def delete_photo(
        event_id: int
    ) -> None:
        photo_path = Event.photo_path(event_id)

        if exists(photo_path):
            remove(photo_path)

    def format(
        event: dict[str, Any]
    ) -> dict[str, Any]:
        event_id = event["id"]

        formatted = {
            "photo_path": Event.photo_path(event_id),

            "text": (
                f"<b>{event['title']}</b>\n\n"
                f"📅 <b>Дата:</b> {event['date']}\n"
                f"🕘 <b>Время:</b> {event['time']}\n"
                f"🌍 <b>Место:</b> {event['place']}\n\n"
                f"{event['description']}\n\n"
            ),

            "reply_markup": InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text=f"👍 {len(event['likes'])}",
                    callback_data=f"{Event.like.__name__} {event_id}"
                ),

                InlineKeyboardButton(
                    text=f"👎 {len(event['dislikes'])}",
                    callback_data=f"{Event.dislike.__name__} {event_id}"
                )],

                [InlineKeyboardButton(
                    text="👁️ Подробнее",
                    url=event["url"]
                )]
            ])
        }

        for tag in event["hashtag"]:
            formatted["text"] += f"{tag} "

        return formatted

    def publish(
        update: Update,
        context: CallbackContext
    ) -> None:
        event = {
            "id": context.user_data["id"],
            "title": context.user_data["title"],
            "date": context.user_data["date"],
            "time": context.user_data["time"],
            "place": context.user_data["place"],
            "description": context.user_data["description"],
            "url": context.user_data["url"][0],
            "hashtag": context.user_data["hashtag"],
            "admin": Bot.from_whom(update).username,
            "likes": [],
            "dislikes": [],
            "messages": []
        }

        channels = Pyson.read_json(CHANNELS_FILE)
        formatted = Event.format(event)

        for channel in channels:
            message = Bot.send_message(
                update, context,
                formatted["text"],
                formatted["reply_markup"],
                formatted["photo_path"],
                channel["id"]
            )

            event["messages"].append(message.to_dict())

        Pyson.append_json(EVENTS_FILE, event)

    def feedback(
        update: Update,
        context: CallbackContext,
        event_id: int,
        dislike: bool = False
    ) -> None:
        bot = context.bot
        reactions = ["likes", "dislikes"]

        user_id = Bot.from_whom(update).id
        event = Pyson.find_object(EVENTS_FILE, event_id)

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
                text=f"👍 {len(event['likes'])}",
                callback_data=f"{Event.like.__name__} {event_id}"
            ),

            InlineKeyboardButton(
                text=f"👎 {len(event['dislikes'])}",
                callback_data=f"{Event.dislike.__name__} {event_id}"
            )],

            [InlineKeyboardButton(
                text="👁️ Подробнее",
                url=event["url"]
            )]
        ])

        for message in event["messages"]:
            message = Message.de_json(message, bot)

            bot.edit_message_reply_markup(
                message.chat_id,
                message.message_id,
                reply_markup=markup
            )

        try:
            bot.edit_message_reply_markup(
                update.effective_chat.id,
                update.callback_query.message.message_id,
                reply_markup=markup
            )
        except:
            pass

        Pyson.erase_json(EVENTS_FILE, event_id)
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
