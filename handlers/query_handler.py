from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler
)

from telegram import Update
from classes.bot import Bot

from commands.help import help
from commands.start import start
from commands.grant import grant
from commands.events import events
from commands.create import create
from commands.delete import delete
from commands.attach import attach
from commands.detach import detach
from commands.admins import admins
from commands.revoke import revoke
from commands.channels import channels

from typing import Any


def callback_query_handler(
    update: Update,
    context: CallbackContext
) -> Any:
    query = update.callback_query
    data = query.data.split()

    if data[0] == Bot.like:
        return Bot.like_event(update, context, data[1])
    elif data[0] == Bot.dislike:
        return Bot.dislike_event(update, context, data[1])

    Bot.check_admin(update, context)
    query.answer()

    if len(data) > 1:
        return globals()[data[0]](update, context, data[1])

    return globals()[data[0]](update, context)


QUERY_HANDLER = CallbackQueryHandler(callback_query_handler)
