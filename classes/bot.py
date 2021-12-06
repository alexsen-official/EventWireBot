from telegram import (
    Update,
    ParseMode,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from telegram.user import User
from classes.pyson import Pyson
from telegram.message import Message


from os import makedirs

from os.path import (
    exists,
    splitext
)

from typing import (
    Any,
    Tuple,
    Iterable,
    BinaryIO
)

from config import (
    ADMINS_FILE,
    CHANNELS_FILE,
    EVENTS_FILE,
    THUMBNAILS_DIRECTORY
)


messages: list[Message] = []


def signal_last(
    iterable: Iterable[Any]
) -> Iterable[Tuple[bool, Any]]:
    iterator = iter(iterable)
    next_value = next(iterator)

    for value in iterator:
        yield [False, next_value]
        next_value = value

    yield [True, next_value]


def from_whom(
    update: Update
) -> User:
    reply = update.message

    if not reply:
        reply = update.callback_query

    return reply.from_user


def send_message(
    update: Update,
    context: CallbackContext,
    text: str,
    markup: InlineKeyboardMarkup = None,
    chat_id: int = None,
    blank: bool = True,
    check: bool = True
) -> Message:
    if chat_id is None:
        chat_id = update.effective_chat.id

    if check:
        check_admin(update, context)

    if blank:
        delete_messages(update, context)

    return edit_previous_message(update, context, text, markup)


def delete_message(
    update: Update,
    context: CallbackContext,
    message_id: int,
    chat_id: int = None
) -> bool:
    bot = context.bot

    if chat_id is None:
        chat_id = update.effective_chat.id

    try:
        return bot.delete_message(chat_id, message_id)
    except:
        return False


def delete_messages(
    update: Update,
    context: CallbackContext
) -> None:
    if update.message:
        delete_message(update, context, update.message.message_id)

    if len(messages) > 1:
        for message in messages[:-1]:
            delete_message(update, context, message.message_id)
            messages.remove(message)


def edit_previous_message(
    update: Update,
    context: CallbackContext,
    text: str,
    markup: InlineKeyboardMarkup = None
) -> None:
    try:
        messages[-1] = context.bot.edit_message_text(
            message_id=messages[-1].message_id,
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    except:
        messages.append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        )

    return messages[-1]


def check_admin(
    update: Update,
    context: CallbackContext
) -> int:
    username = from_whom(update).username

    for admin in Pyson.read(ADMINS_FILE):
        if username == admin["username"]:
            return ConversationHandler.END

    delete_messages(update, context)

    response = (
        "❌ <b>Отказано в доступе!</b>\n"
        "Вы не являетесь администатором!"
    )

    send_message(update, context, response, check=False)
    exit()


def dislike(
    update: Update,
    context: CallbackContext,
    event_id: int
) -> None:
    like(update, context, event_id, reverse=True)


def like(
    update: Update,
    context: CallbackContext,
    event_id: int,
    reverse: bool = False
) -> None:
    bot = context.bot
    event_id = int(event_id)
    events = Pyson.read(EVENTS_FILE)
    user_id = from_whom(update).id
    reactions = ["liked", "disliked"]

    if reverse:
        reactions.reverse()

    for event in events:
        if event["id"] == event_id:
            if user_id in event[reactions[0]]:
                event[reactions[0]].remove(user_id)
            else:
                event[reactions[0]].append(user_id)

                if user_id in event[reactions[1]]:
                    event[reactions[1]].remove(user_id)

            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=f"👍 {len(event['liked'])}",
                    callback_data=f"{like.__name__} {event_id}"
                ),

                    InlineKeyboardButton(
                    text=f"👎 {len(event['disliked'])}",
                    callback_data=f"{dislike.__name__} {event_id}"
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

            Pyson.erase(EVENTS_FILE, id=event_id)
            Pyson.append(EVENTS_FILE, event)

            break


def format_event(
    context: CallbackContext
) -> dict[str, Any]:
    event_id = context.user_data["id"]

    caption = (
        f"<b>{context.user_data['title']}</b>\n\n"
        f"📅 <b>Дата:</b> {context.user_data['date']}\n"
        f"🕘 <b>Время:</b> {context.user_data['time']}\n"
        f"🌍 <b>Место:</b> {context.user_data['place']}\n\n"
        f"{context.user_data['description']}"
    )

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="👍 0",
            callback_data=f"{like.__name__} {event_id}"
        ),

            InlineKeyboardButton(
            text="👎 0",
            callback_data=f"{like.__name__} {event_id}"
        )],

        [InlineKeyboardButton(
            text="👁️ Подробнее",
            url=context.user_data["url"]
        )]
    ])

    return {
        "caption": caption,
        "markup": markup
    }


def publish_event(
    update: Update,
    context: CallbackContext
) -> list[dict[str, int]]:
    bot = context.bot
    channels = Pyson.read(CHANNELS_FILE)
    event_id = context.user_data["id"]

    if channels:
        event = format_event(context)
        event["published"] = []

        for channel in channels:
            sent_message = bot.send_photo(
                chat_id=channel["id"],
                caption=event["caption"],
                reply_markup=event["markup"],
                photo=open(f"{THUMBNAILS_DIRECTORY}/{event_id}.jpg", "rb"),
                parse_mode=ParseMode.HTML
            )

            event["published"].append({
                "chat_id": sent_message.chat_id,
                "message_id": sent_message.message_id
            })

        return event["published"]

    return []


def save_event(
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
        "url": context.user_data["url"],
        "liked": [],
        "disliked": [],
        "created": from_whom(update).username,
        "published": publish_event(update, context)
    }

    Pyson.append(EVENTS_FILE, event)


def download_thumbnail(
    update: Update,
    context: CallbackContext
) -> bool:
    if not exists(THUMBNAILS_DIRECTORY):
        makedirs(THUMBNAILS_DIRECTORY)

    try:
        file_id = update.message.photo[-1].file_id
        event_id = context.user_data["id"]

        thumbnail = context.bot.get_file(file_id)
        thumbnail.download(f"{THUMBNAILS_DIRECTORY}/{event_id}.jpg")
    except:
        return False

    return True
