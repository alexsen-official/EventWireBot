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
    ) -> bool:
        bot = context.bot
        chat_id = update.effective_chat.id
        user = Bot.from_whom(update)
        admin = Pyson.find_object(ADMINS_FILE, user.username)

        if admin is None:
            text = (
                "❌ <b>Отказано в доступе!</b>\n"
                "Вы не являетесь администатором!"
            )

            bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML
            )

            return False

        if "id" not in admin.keys():
            admin["id"] = user.id

        Pyson.erase_json(ADMINS_FILE, user.username)
        Pyson.append_json(ADMINS_FILE, admin)

        return True

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
        reply_markup: InlineKeyboardMarkup = None,
        photo_path: str = None,
        chat_id: int = None,
        blank: bool = False
    ) -> Message:
        bot = context.bot
        sent_message = None
        query = update.callback_query

        if Bot.check_admin(update, context):
            if chat_id is None:
                chat_id = update.effective_chat.id

            if query and not blank:
                try:
                    sent_message = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=query.message.message_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    sent_message = bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )
            else:
                try:
                    photo = open(photo_path, "rb")

                    sent_message = bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    sent_message = bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )

        return sent_message

    def delete_message(
        update: Update,
        context: CallbackContext,
        message: Message
    ) -> bool:
        if message:
            bot = context.bot
            chat_id = message.chat.id
            message_id = message.message_id

            try:
                return bot.delete_message(chat_id, message_id)
            except:
                return False
