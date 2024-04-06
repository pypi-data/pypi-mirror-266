from dataclasses import dataclass


@dataclass
class Arguments:
    inst_path: str
    cfg_ha_path: str


@dataclass
class EnvField:
    Env: list


@dataclass
class ConfigField:
    Config: EnvField


@dataclass
class SupervisorApi(ConfigField):
    SUPERVISOR_TOKEN: str | None

    def __get_token_iteration(self):
        for it in self.Config.Env:
            if "SUPERVISOR_TOKEN" in it:
                return "Bearer " + it.replace("SUPERVISOR_TOKEN=", "")

    def get_supervisor_token(self):
        self.SUPERVISOR_TOKEN = self.__get_token_iteration()
