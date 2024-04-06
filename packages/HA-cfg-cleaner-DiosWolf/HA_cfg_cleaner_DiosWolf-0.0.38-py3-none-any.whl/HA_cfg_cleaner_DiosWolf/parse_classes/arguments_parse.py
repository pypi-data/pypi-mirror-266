import sys
from typing import TypeVar, Type, LiteralString
from dacite import from_dict
from HA_cfg_cleaner_DiosWolf.data_classes_json.args_parse import Arguments
from os.path import join, dirname


class ConsoleArguments:
    T = TypeVar("T")
    args: Arguments

    def __init__(self):
        self.args = self.__get_args(Arguments)

    def __get_args_dict(self) -> dict[str, str | LiteralString | bytes]:
        args_dict = {}
        for arg in sys.argv:
            if "instr" in arg:
                args_dict["inst_path"] = arg

            if "config_HA.json" in arg:
                args_dict["cfg_ha_path"] = arg

        if "inst_path" not in args_dict.keys():
            # args_dict["inst_path"] = "instructions.yaml"
            raise Exception("Cant find instructions file")

        if "cfg_ha_path" not in args_dict.keys():
            cfg_path = dirname(__file__).replace("instruction_classes", "")
            cfg_path = cfg_path.replace("parse_classes", "")
            args_dict["cfg_ha_path"] = join(cfg_path, "configs_HA/config_HA.json")

            # args_dict["cfg_ha_path"] = (
            #     "C:\\MyFiles\\Python work\\work_python_pipenv\\HA_cfg_cleaner_DiosWolf\\HA_cfg_cleaner_DiosWolf\\configs_HA\\config_HA_wind.json"
            # )
        return args_dict

    def __get_args(self, data_class: Type[T]) -> T:
        args_dict = self.__get_args_dict()
        return from_dict(data_class=data_class, data=args_dict)
