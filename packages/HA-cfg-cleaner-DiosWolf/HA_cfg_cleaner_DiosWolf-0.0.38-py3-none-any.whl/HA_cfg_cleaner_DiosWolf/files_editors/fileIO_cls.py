from ruamel.yaml import YAML
import json
from typing import Type, TypeVar, Union
from dacite import from_dict
from HA_cfg_cleaner_DiosWolf.parse_classes.parse_cls import ParseFileInfo


class FileIO:
    T = TypeVar("T")

    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.json = json
        self.parser = ParseFileInfo()

        self.read_functions = {
            ".yaml": self.yaml_read,
            ".json": self.json_read,
            "byte_lines": self.read_byte_lines,
            "all_lines": self.read_all_lines,
        }
        self.write_functions = {
            ".yaml": self.yaml_write,
            ".json": self.json_write,
            "all_lines": self.write_lines,
        }

    def yaml_read(self, path: str, data_class: Type[T] = None) -> Union[T, dict]:
        with open(path, "r", encoding="utf-8") as reader:
            data = self.yaml.load(reader)

            if data_class:
                return from_dict(data_class=data_class, data=data)

            return data

    def yaml_write(self, path: str, file: any):
        with open(path, "w", encoding="utf8") as writer:
            self.yaml.dump(file, writer)

    def json_read(self, path: str, data_class: Type[T] = None) -> Union[T, dict]:
        with open(path, "rb") as reader:
            data = self.json.load(reader)

            if data_class:
                return from_dict(data_class=data_class, data=data)

            return data

    def json_write(self, path: str, file: any):
        with open(path, "w", encoding="utf8") as writer:
            self.json.dump(file, writer, indent=2, sort_keys=False, ensure_ascii=False)

    def read_byte_lines(self, path: str, _: None) -> list[bytes]:
        with open(path, "rb") as file:
            return file.readlines()

    def read_all_lines(self, path: str, _: None) -> list[str]:
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()

    def write_lines(self, path: str, lines_list: list[any]):
        with open(path, "w", encoding="utf-8") as writer:
            writer.writelines(lines_list)

    def read_with_type(
        self, path: str, file_type: str = None, data_class: Type[T] = None
    ) -> Union[T, dict]:
        if file_type is None:
            file_type = self.parser.get_type(path)

        read_function: classmethod | None = self.read_functions.get(file_type)

        if read_function:
            return read_function(path, data_class)

        raise ValueError(f"Unsupported file type: {file_type}")

    def write_with_type(self, path: str, file: any, file_type: str = None):
        if file_type is None:
            file_type = self.parser.get_type(path)

        write_function = self.write_functions.get(file_type)

        if write_function:
            write_function(path, file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
