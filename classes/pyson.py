from os import (
    walk,
    makedirs
)

from os.path import (
    isdir,
    exists
)

from json import (
    load,
    dump
)

from typing import Any
from sys import maxsize
from config import ENCODING


class Pyson:
    def read_json(
        path: str
    ) -> list[dict[str, Any]]:
        if not exists(path):
            return []

        with open(path, "r", encoding=ENCODING) as file:
            data = load(file)

        return data

    def write_json(
        path: str,
        data: list[dict[str, Any]]
    ) -> None:
        Pyson.make_dirs(path)

        with open(path, "w", encoding=ENCODING) as file:
            dump(data, file)

    def append_json(
        path: str,
        object: dict[str, Any]
    ) -> None:
        data = Pyson.read_json(path)
        data.append(object)

        Pyson.write_json(path, data)

    def erase_json(
        path: str,
        *args: list[Any]
    ) -> None:
        data = Pyson.read_json(path)
        object = Pyson.find_object(path, *args)

        if object in data:
            data.remove(object)
            Pyson.write_json(path, data)

    def find_object(
        path: str,
        *args: list[Any]
    ) -> dict[str, Any]:
        data = Pyson.read_json(path)

        for object in data:
            for value in args:
                if value in object.values():
                    return object

        return None

    def make_dirs(
        path: str
    ) -> None:
        for index, character in enumerate(path):
            if character == "/":
                directory = path[:index]

                if not exists(directory):
                    makedirs(directory)

    def generate_id(
        path: str
    ) -> int:
        for id in range(1, maxsize):
            if Pyson.find_object(path, id) is None:
                return id
