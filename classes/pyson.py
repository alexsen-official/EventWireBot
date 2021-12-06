from typing import Any
from os import makedirs
from os.path import exists
from json import load, dump


class Pyson:
    def read(
        path: str
    ) -> list[dict[str, Any]]:
        if not exists(path):
            return []

        with open(path, "r", encoding="UTF-8") as file:
            data = load(file)

        return data

    def write(
        path: str,
        data: list[dict[str, Any]]
    ) -> None:
        for index, character in enumerate(path):
            if character == "/":
                directory = path[:index]

                if not exists(directory):
                    makedirs(directory)

        with open(path, "w", encoding="UTF-8") as file:
            dump(data, file)

    def append(
        path: str,
        object: dict[str, Any]
    ) -> None:
        data = Pyson.read(path)
        data.append(object)

        Pyson.write(path, data)

    def erase(
        path: str,
        **kwargs
    ) -> None:
        data = Pyson.read(path)

        for object in data:
            for key, value in kwargs.items():
                if key not in object.keys():
                    continue

                if object[key] == value:
                    data.remove(object)
                    Pyson.write(path, data)
