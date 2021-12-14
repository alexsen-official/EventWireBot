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
        state = context.user_data["state"]

        if state in ["title", "date", "time", "place", "description"]:
            context.user_data[state] = message.text
        elif state in ["url", "hashtag"]:
            entities = message.parse_entities(state).values()
            context.user_data[state] = list(entities)
        elif state == "thumbnail":
            context.user_data[state] = Event.download_photo(update, context)

        if context.user_data[state]:
            state = CREATE_COMMAND.next_state(state)
        else:
            Bot.send_message(
                update, context,
                CREATE_COMMAND.states["error"]
            )
    else:
        context.user_data["id"] = Event.generate_id()
        state = CREATE_COMMAND.next_state()

    context.user_data["state"] = state

    if state == "success":
        Event.publish(update, context)

        Bot.send_message(
            update, context,
            CREATE_COMMAND.states[state],
            CREATE_COMMAND.markup
        )

        return ConversationHandler.END

    Bot.send_message(
        update, context,
        CREATE_COMMAND.states[state]
    )

    return CREATE_COMMAND.id


CREATE_COMMAND = Command(
    callback=create,
    description="➕ Создать мероприятие",

    states={
        "title": "🔖 Введите название мероприятия: ",
        "date": "📅 Введите дату проведения мероприятия: ",
        "time": "🕘 Введите время проведения мероприятия: ",
        "place": "🌍 Введите место проведения мероприятия: ",
        "description": "📝 Введите краткое описание мероприятия: ",
        "url": "🔗 Введите ссылку на мероприятие: ",
        "thumbnail": "🖼️ Загрузите изображение мероприятия: ",
        "hashtag": "#️⃣ Введите теги мероприятия: ",

        "success": "✅ <b>Мероприятие успешно опубликовано во всех привязанных к боту каналах!</b>",
        "error": "❌ <b>Проверьте правильность введенных вами данных!</b>"
    },

    markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=BACK_COMMAND.description,
            callback_data=BACK_COMMAND.name
        )]
    ])
)
