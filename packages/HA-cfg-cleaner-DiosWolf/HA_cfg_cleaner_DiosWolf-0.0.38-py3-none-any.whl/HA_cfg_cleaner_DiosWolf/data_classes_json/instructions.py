from dataclasses import dataclass


# TODO: for instructions file
@dataclass
class BasePath:
    path: str


@dataclass
class BaseListIds:
    ids_list: list[str]


@dataclass
class DeleteObjects(BasePath):
    objects_names: list[str]


@dataclass
class DeleteScript(BasePath):
    scripts_ids: list[str]


@dataclass
class DeleteObjects(BasePath):
    objects_names: list[str]


@dataclass
class CleanFolders(BasePath):
    folders_names: list[str]


@dataclass
class CleanFiles(BasePath):
    files_names: list[str]


@dataclass
class ChangeFiles(BasePath):
    new_content: list


@dataclass
class FindInFiles:
    report_path: str | None
    text_to_find: list[str]


@dataclass
class HostInst:
    api_key: str
    host: str | None
    port: str | None


@dataclass
class DisableAutomations(BaseListIds):
    host_info: HostInst | None


@dataclass
class ChangeAddonsOptions:
    addon_id: str
    addon_options: dict


@dataclass
class Instructions:
    delete_integrations: BaseListIds
    enable_integration: BaseListIds
    disable_integration: BaseListIds
    delete_automations: BaseListIds
    delete_objects: list[DeleteObjects]
    delete_script: list[DeleteScript]
    clean_folders: list[CleanFolders]
    clean_files: list[CleanFiles]
    change_files: list[ChangeFiles]
    find_in_all_files: FindInFiles
    disable_automations: DisableAutomations
    disable_addons: BaseListIds
    delete_addons: BaseListIds
    change_addons_options: list[ChangeAddonsOptions]
