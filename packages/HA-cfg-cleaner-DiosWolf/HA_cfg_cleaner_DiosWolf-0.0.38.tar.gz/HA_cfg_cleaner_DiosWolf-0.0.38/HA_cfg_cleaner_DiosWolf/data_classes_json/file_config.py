# TODO: for file configurations
from dataclasses import dataclass


@dataclass
class Configuration:
    config_id: str
    filename: str
    first_key: str | None
    second_key: str | None
    id_key: str
    identifiers_key: str
    type_cfg: str
    path: str
    on_off_field: str
    on_integration: None | str
    off_integration: str


@dataclass
class ConfigRestoreState:
    config_id: str
    filename: str
    first_key: str | None
    second_key: str | None
    id_key: str
    state: str
    attr_id: str
    identifiers_key: str
    type_cfg: str
    path: str
    on_off_field: str
    on_integration: None | str
    off_integration: str


@dataclass
class HostInfo:
    api_key: str
    host: str
    port: str
    automations_off_url: str
    addons_options_url: str


@dataclass
class SshCommands:
    delete_addons: list[str]
    disable_addons: list[str]
    change_cfg_addons: list[str]
    get_supervisor_api: list[str]


@dataclass
class ConfigurationFile:
    configurations: list[Configuration]
    automations_cfg: list[Configuration]
    config_restore_state: ConfigRestoreState
    host_info: HostInfo
    ssh_commands: SshCommands
