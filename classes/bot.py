from telegram import (
    User,
    Chat,
    Update,
    Message,
    ParseMode,
    InlineKeyboardMarkup
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

from json import loads
from urllib.request import urlopen

from config import (
    BOT_TOKEN,
    ADMINS_FILE
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
        photo_path: str = None,
        chat_id: int = None
    ) -> Message:
        bot = context.bot

        if chat_id is None:
            chat_id = update.effective_chat.id

        if photo_path is None:
            sent_message = bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )

            Bot.messages.append(sent_message)
        else:
            photo = open(photo_path, "rb")

            sent_message = bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )

        return sent_message

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

        if Bot.messages:
            previous_message = Bot.messages[-1]

            if previous_message.text == text and previous_message.reply_markup == markup:
                return previous_message

        if chat_id is None:
            chat_id = update.effective_chat.id

        if message in Bot.messages:
            Bot.messages.remove(message)

        edited_message = bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )

        Bot.messages.append(edited_message)
        return edited_message

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
        message: Message
    ) -> bool:
        if message:
            bot = context.bot
            chat_id = message.chat.id
            message_id = message.message_id

            if message in Bot.messages:
                Bot.messages.remove(message)

            try:
                return bot.delete_message(chat_id, message_id)
            except:
                return False

    def delete_previous_message(
        update: Update,
        context: CallbackContext
    ) -> bool:
        previous_message = Bot.messages[-1]
        return Bot.delete_message(update, context, previous_message)

    def delete_user_message(
        update: Update,
        context: CallbackContext
    ) -> bool:
        user_message = update.message
        return Bot.delete_message(update, context, user_message)

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
