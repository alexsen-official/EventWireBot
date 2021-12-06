from typing import Callable
from telegram.ext import Filters
from telegram.message import Message
from telegram import InlineKeyboardMarkup


class Command:
    commands: list = []

    def __init__(
        self,
        name: str = None,
        callback: Callable = None,
        description: str = None,
        markup: InlineKeyboardMarkup = None,
        states: dict[str, str] = {},
        hidden: bool = False
    ) -> None:
        self.name = name
        self.callback = callback
        self.description = description
        self.markup = markup
        self.states = states
        self.hidden = hidden

        if name is None and callback is not None:
            self.name = callback.__name__

        if not hidden:
            self.commands.append(self)

    def filter(
        message: Message
    ) -> bool:
        return Filters._Command.filter(Filters._Command, message)

    def next_state(
        self,
        current_state: str = None
    ) -> str:
        states = list(self.states)

        if not states:
            return None

        if current_state in states:
            return states[states.index(current_state) + 1]
        else:
            return states[0]
