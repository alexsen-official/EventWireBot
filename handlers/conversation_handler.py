from telegram.ext import (
    Filters,
    MessageHandler,
    CommandHandler,
    ConversationHandler
)

from commands.grant import GRANT_COMMAND
from commands.create import CREATE_COMMAND
from commands.attach import ATTACH_COMMAND
from commands.cancel import CANCEL_COMMAND
from handlers.query_handler import QUERY_HANDLER


CONVERSATION_HANDLER = ConversationHandler(
    entry_points=[
        QUERY_HANDLER,
        CommandHandler(GRANT_COMMAND.name, GRANT_COMMAND.callback),
        CommandHandler(CREATE_COMMAND.name, CREATE_COMMAND.callback),
        CommandHandler(ATTACH_COMMAND.name, ATTACH_COMMAND.callback)
    ],

    states={
        GRANT_COMMAND.name: [MessageHandler(
            Filters.all & ~Filters.command, GRANT_COMMAND.callback
        )],

        CREATE_COMMAND.name: [MessageHandler(
            Filters.all & ~Filters.command, CREATE_COMMAND.callback
        )],

        ATTACH_COMMAND.name: [MessageHandler(
            Filters.all & ~Filters.command, ATTACH_COMMAND.callback
        )]
    },

    fallbacks=[MessageHandler(Filters.command, CANCEL_COMMAND.callback)]
)
