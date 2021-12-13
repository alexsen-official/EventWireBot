from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from classes.bot import Bot
from classes.event import Event
from classes.command import Command

from commands.back import BACK_COMMAND


def create(
    update: Update,
    context: CallbackContext
) -> int:
    message = update.message

    if "state" in context.user_data.keys():
        response = ""
        state = context.user_data["state"]

        if state in ["title", "date", "time", "place", "description"]:
            context.user_data[state] = message.text
            response = f" <b>{message.text}</b>"
        elif state == "url":
            urls = list(message.parse_entities("url").values())

            if urls:
                url = urls[0]
                context.user_data[state] = url
                response = f" <b><a href='{url}'>ссылка</a></b>"
        elif state == "thumbnail":
            if Event.download_photo(update, context):
                response = " <b>изображение</b>"

        if response:
            state = CREATE_COMMAND.next_state(state)
        else:
            Bot.send_message(
                update, context,
                CREATE_COMMAND.states["error"]
            )
    else:
        state = CREATE_COMMAND.next_state()
        context.user_data["id"] = Event.generate_id()

    context.user_data["state"] = state

    if state == "success":
        id = Event.save(update, context)
        Event.publish(update, context, id)

        Bot.send_message(
            update, context,
            CREATE_COMMAND.states[state],
            CREATE_COMMAND.markup
        )

        return ConversationHandler.END
    else:
        Bot.send_message(
            update, context,
            CREATE_COMMAND.states[state]
        )

        return CREATE_COMMAND.id


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
