from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler
)

from classes.command import Command

from config import BOT_TOKEN
from commands.undefined import UNDEFINED_COMMAND
from handlers.query_handler import QUERY_HANDLER
from handlers.conversation_handler import CONVERSATION_HANDLER


def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    for command in Command.commands:
        dispatcher.add_handler(CommandHandler(
            command.name, command.callback
        ))

    dispatcher.add_handler(CONVERSATION_HANDLER)
    dispatcher.add_handler(QUERY_HANDLER)

    dispatcher.add_handler(MessageHandler(
        Filters.command, UNDEFINED_COMMAND.callback
    ))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
