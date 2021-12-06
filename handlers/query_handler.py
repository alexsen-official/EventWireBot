from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler
)

from telegram import Update

from classes.bot import like
from commands.help import help
from classes.bot import dislike
from commands.start import start
from commands.grant import grant
from commands.events import events
from commands.create import create
from commands.delete import delete
from commands.attach import attach
from commands.detach import detach
from commands.admins import admins
from commands.revoke import revoke
from classes.bot import check_admin
from commands.channels import channels

from typing import Any


def callback_query_handler(
    update: Update,
    context: CallbackContext
) -> Any:
    query = update.callback_query
    query.answer()

    data = query.data.split()
    callback = data[0]

    if callback == str(None):
        return None

    if callback != like.__name__ and callback != dislike.__name__:
        check_admin(update, context)

    if len(data) > 1:
        return globals()[callback](update, context, data[1])

    return globals()[callback](update, context)


QUERY_HANDLER = CallbackQueryHandler(callback_query_handler)
