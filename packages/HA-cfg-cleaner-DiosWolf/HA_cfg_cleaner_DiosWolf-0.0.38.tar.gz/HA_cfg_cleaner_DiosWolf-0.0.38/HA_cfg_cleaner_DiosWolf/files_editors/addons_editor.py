import os
from json import loads
from subprocess import run, CompletedProcess, PIPE

from dacite import from_dict

from HA_cfg_cleaner_DiosWolf.castom_errors.castom_errors import CustomError
from HA_cfg_cleaner_DiosWolf.data_classes_json.args_parse import SupervisorApi
from HA_cfg_cleaner_DiosWolf.data_classes_json.file_config import SshCommands, HostInfo
from HA_cfg_cleaner_DiosWolf.files_editors.fileIO_cls import FileIO
from HA_cfg_cleaner_DiosWolf.ha_requests.ha_request import HARequests


class AddonsEditor:
    def __init__(self, configuration: SshCommands = None, host_info: HostInfo = None):
        if SshCommands:
            self.configuration = configuration
            self.file_io = FileIO()

        if host_info:
            self.host_info = host_info
            host_info.api_key = self.__get_supervision_api().SUPERVISOR_TOKEN
            self.ha_request = HARequests(host_info, host_info.api_key)

    def __send_ssh_command(self, command: list[str]) -> CompletedProcess[str]:
        return run(command, stdout=PIPE, text=True)

    def __get_command(self, command: list[str], addon_id: str) -> list[str]:
        return command + [addon_id]

    def __get_supervision_api(self) -> SupervisorApi:
        ans = self.__send_ssh_command(self.configuration.get_supervisor_api)
        as_dict = loads(ans.stdout)[0]
        supervisor_api = from_dict(data_class=SupervisorApi, data=as_dict)
        supervisor_api.get_supervisor_token()
        return supervisor_api

    def write_new_cfg(self, cfg_path: str, cfg_name: str, new_cfg: dict):
        os.mkdir(cfg_path)
        self.file_io.yaml_write(cfg_path + cfg_name, new_cfg)

    def use_ssh_addon(self, addon_id: str, command: list[str]):
        command = self.__get_command(command, addon_id)
        if (result := self.__send_ssh_command(command)).returncode:
            raise CustomError(result.stdout)

    def stop_autoboot(self, addon_id: str):
        url = self.host_info.addons_options_url.format(addon_id=addon_id)
        headers = {"content-type": "application/json"}
        data = {"boot": "manual"}
        self.ha_request.post_requests(url, data, headers)

    def change_addon_options(self, addon_id: str, options: dict[str:any]):
        url = self.host_info.addons_options_url.format(addon_id=addon_id)
        headers = {"content-type": "application/json"}
        data = {"options": options}
        self.ha_request.post_requests(url, data, headers)
