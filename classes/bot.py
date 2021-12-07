from sys import path
from telegram import (
    User,
    Chat,
    Update,
    Message,
    ParseMode,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from typing import (
    Any,
    Tuple,
    Iterable
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from classes.pyson import Pyson

from os import (
    walk,
    remove,
    makedirs
)

from os.path import (
    isdir,
    exists
)

from json import loads
from urllib.request import urlopen

from config import (
    BOT_TOKEN,
    EVENTS_FILE,
    ADMINS_FILE,
    CHANNELS_FILE,
    THUMBNAILS_FORMAT,
    THUMBNAILS_DIRECTORY
)


class Bot:
    messages: list[Message] = []

    def get_chat(
        context: CallbackContext,
        url: str
    ) -> Chat:
        domain = ".me/"
        bot = context.bot
        mention = url[url.find(domain) + len(domain):]
        query = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?text=!&chat_id=@{mention}"

        try:
            with urlopen(query) as page:
                data = loads(page.read().decode())

                chat_id = data["result"]["chat"]["id"]
                message_id = data["result"]["message_id"]

                chat = bot.get_chat(chat_id)
                bot.delete_message(chat_id, message_id)

                return chat
        except:
            return None

    def from_whom(
        update: Update
    ) -> User:
        message = update.message

        if not message:
            return update.callback_query.from_user

        return message.from_user

    def check_admin(
        update: Update,
        context: CallbackContext
    ) -> int:
        username = Bot.from_whom(update).username
        admin = Pyson.find_object(ADMINS_FILE, username)

        text = (
            "❌ <b>Отказано в доступе!</b>\n"
            "Вы не являетесь администатором!"
        )

        if username in admin.values():
            return ConversationHandler.END

        Bot.send_message(update, context, text)
        exit()

    def signal_last(
        iterable: Iterable[Any]
    ) -> Iterable[Tuple[bool, Any]]:
        iterator = iter(iterable)
        next_item = next(iterator)

        for item in iterator:
            yield [False, next_item]
            next_item = item

        yield [True, next_item]

    def send_message(
        update: Update,
        context: CallbackContext,
        text: str,
        markup: InlineKeyboardMarkup = None,
        chat_id: int = None
    ) -> Message:
        bot = context.bot

        if chat_id is None:
            chat_id = update.effective_chat.id

        Bot.messages.append(
            bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        )

        return Bot.messages[-1]

    def edit_message(
        update: Update,
        context: CallbackContext,
        message: Message,
        text: str,
        markup: InlineKeyboardMarkup = None,
        chat_id: int = None
    ) -> Message:
        bot = context.bot
        message_id = message.message_id

        if chat_id is None:
            chat_id = update.effective_chat.id

        if message in Bot.messages:
            Bot.messages.remove(message)

        Bot.messages.append(
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
        )

        return Bot.messages[-1]

    def edit_previous_message(
        update: Update,
        context: CallbackContext,
        text: str,
        markup: InlineKeyboardMarkup = None
    ) -> Message:
        Bot.delete_user_message(update, context)

        if Bot.messages:
            previous_message = Bot.messages[-1]
            return Bot.edit_message(update, context, previous_message, text, markup)

        return Bot.send_message(update, context, text, markup)

    def delete_message(
        update: Update,
        context: CallbackContext,
        message: Message,
        chat_id: int = None
    ) -> bool:
        if message:
            bot = context.bot

            if chat_id is None:
                chat_id = update.effective_chat.id

            if message in Bot.messages:
                Bot.messages.remove(message)

            try:
                return bot.delete_message(
                    chat_id=chat_id,
                    message_id=message.message_id
                )
            except:
                return False

    def delete_user_message(
        update: Update,
        context: CallbackContext
    ) -> bool:
        message = update.message
        return Bot.delete_message(update, context, message)

    def delete_bot_messages(
        update: Update,
        context: CallbackContext
    ) -> None:
        for message in Bot.messages[:-1]:
            Bot.delete_message(update, context, message)

    def delete_all_messages(
        update: Update,
        context: CallbackContext
    ) -> None:
        Bot.delete_bot_messages(update, context)
        Bot.delete_user_message(update, context)

    def get_thumbnail_path(
        event_id: int
    ) -> str:
        file_name = f"{event_id}.{THUMBNAILS_FORMAT}"
        file_path = THUMBNAILS_DIRECTORY + file_name

        return file_path

    def download_thumbnail(
        update: Update,
        context: CallbackContext
    ) -> bool:
        bot = context.bot
        message = update.message

        Pyson.make_dirs(THUMBNAILS_DIRECTORY)

        try:
            event_id = context.user_data["id"]

            file_id = message.photo[-1].file_id
            file_path = Bot.get_thumbnail_path(event_id)

            file = bot.get_file(file_id)
            file.download(file_path)
        except:
            return False

        return True

    def delete_thumbnail(
        event_id: int
    ) -> bool:
        file_path = Bot.get_thumbnail_path(event_id)

        if exists(file_path):
            remove(file_path)
            return True

        return False

    def get_formatted_event(
        event: dict[str, Any]
    ) -> dict[str, Any]:
        formatted_event = {
            "caption": (
                f"<b>{event['title']}</b>\n\n"
                f"📅 <b>Дата:</b> {event['date']}\n"
                f"🕘 <b>Время:</b> {event['time']}\n"
                f"🌍 <b>Место:</b> {event['place']}\n\n"
                f"{event['description']}"
            ),

            "markup": InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="👍 0",
                    callback_data=f"{Bot.like} {event['id']}"
                ),

                InlineKeyboardButton(
                    text="👎 0",
                    callback_data=f"{Bot.dislike} {event['id']}"
                )],

                [InlineKeyboardButton(
                    text="👁️ Подробнее",
                    url=event["url"]
                )]
            ])
        }

        return formatted_event

    def save_event(
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

    def publish_event(
        update: Update,
        context: CallbackContext,
        event_id: int
    ) -> None:
        bot = context.bot

        channels = Pyson.read_json(CHANNELS_FILE)
        event = Pyson.find_object(EVENTS_FILE, event_id)

        formatted_event = Bot.get_formatted_event(event)
        thumbnail_path = Bot.get_thumbnail_path(event_id)

        if channels:
            for channel in channels:
                thumbnail = open(thumbnail_path, "rb")

                sent_message = bot.send_photo(
                    chat_id=channel["id"],
                    caption=formatted_event["caption"],
                    reply_markup=formatted_event["markup"],
                    photo=thumbnail,
                    parse_mode=ParseMode.HTML
                )

                event["published"].append({
                    "chat_id": sent_message.chat_id,
                    "message_id": sent_message.message_id
                })

        Pyson.erase_json(EVENTS_FILE, event_id)
        Pyson.append_json(EVENTS_FILE, event)

    def set_reaction(
        update: Update,
        context: CallbackContext,
        event_id: int,
        dislike: bool = False
    ) -> None:
        bot = context.bot
        event = Pyson.find_object(EVENTS_FILE, event_id)
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
                callback_data=f"{Bot.like} {event_id}"
            ),

            InlineKeyboardButton(
                text=f"👎 {len(event['disliked'])}",
                callback_data=f"{Bot.dislike} {event_id}"
            )],

            [InlineKeyboardButton(
                text="👁️ Подробнее",
                url=event["url"]
            )]
        ])

        for publication in event["published"]:
            bot.edit_message_reply_markup(
                message_id=publication["message_id"],
                chat_id=publication["chat_id"],
                reply_markup=markup
            )

        Pyson.erase_json(EVENTS_FILE, event_id)
        Pyson.append_json(EVENTS_FILE, event)

    def like_event(
        update: Update,
        context: CallbackContext,
        event_id: int
    ) -> None:
        Bot.set_reaction(update, context, int(event_id))

    def dislike_event(
        update: Update,
        context: CallbackContext,
        event_id: int
    ) -> None:
        Bot.set_reaction(update, context, int(event_id), dislike=True)

    like = like_event.__name__
    dislike = dislike_event.__name__
