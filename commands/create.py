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

from classes.pyson import Pyson
from classes.command import Command

from classes.bot import (
    delete_message,
    messages,
    edit_previous_message,
    save_event,
    send_message,
    delete_messages,
    download_thumbnail,
)

from config import EVENTS_FILE
from commands.back import BACK_COMMAND


def create(
    update: Update,
    context: CallbackContext
) -> str:
    message = update.message
    response = ""

    if "state" in context.user_data.keys():
        state = context.user_data["state"]

        if state in ["title", "date", "time", "place", "description"]:
            context.user_data[state] = message.text
            response = f"<b>{message.text}</b>"
        elif state == "url":
            urls = list(message.parse_entities("url").values())

            if urls:
                url = urls[0]
                context.user_data[state] = url
                response = f"<b><a href='{url}'>ссылка</a></b>"
        elif state == "thumbnail":
            if download_thumbnail(update, context):
                response = f"<b>изображение</b>"

        delete_message(update, context, update.message.message_id)

        if response:
            state = CREATE_COMMAND.next_state(state)
            edit_previous_message(
                update, context, f"{messages[-1].text} {response}")
        else:
            edit_previous_message(
                update, context,
                CREATE_COMMAND.states["error"]
            )
    else:
        state = CREATE_COMMAND.next_state()
        events = Pyson.read(EVENTS_FILE)

        if events:
            context.user_data["id"] = events[-1]["id"] + 1
        else:
            context.user_data["id"] = 1

    context.user_data["state"] = state

    if state == "title" or state == "success":
        send_message(
            update, context,
            CREATE_COMMAND.states[state],
            CREATE_COMMAND.markup
        )
    else:
        messages.append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=CREATE_COMMAND.states[state],
                reply_markup=CREATE_COMMAND.markup,
                parse_mode=ParseMode.HTML
            )
        )

    if state == "success":
        save_event(update, context)
        del context.user_data["state"]
        return ConversationHandler.END

    return CREATE_COMMAND.name


CREATE_COMMAND = Command(
    callback=create,
    description="➕ Создать мероприятие",

    states={
        "title": "🔖 Название мероприятия: ",
        "date": "📅 Дата проведения мероприятия: ",
        "time": "🕘 Время проведения мероприятия: ",
        "place": "🌍 Место проведения мероприятия: ",
        "description": "📝 Краткое описание мероприятия: ",
        "url": "🔗 Ссылка на подробную информацию о мероприятии: ",
        "thumbnail": "🖼️ Изображение мероприятия: ",

        "success": "✅ <b>Мероприятие успешно создано!</b>",
        "error": "❌ <b>Некорректно введенные данные!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
