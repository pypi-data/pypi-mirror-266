from HA_cfg_cleaner_DiosWolf.data_classes_json.file_config import ConfigRestoreState


class EditorRestoreFile:
    def __init__(self, configuration: ConfigRestoreState, full_cfg: dict):
        self.configuration = configuration
        self.full_cfg = full_cfg

    def __get_editable_cfg(self) -> list[dict]:
        return self.full_cfg[self.configuration.first_key]

    def __set_editable_cfg(self, edit_cfg_part: list[dict]) -> dict:
        self.full_cfg[self.configuration.first_key] = edit_cfg_part
        return self.full_cfg

    def del_automation_restore_state(self, integrations_list: list[str]) -> dict:
        editable_part = self.__get_editable_cfg()
        new_cfg_list = []

        for config_dict in editable_part:
            try:
                if (
                    config_dict[self.configuration.first_key][
                        self.configuration.identifiers_key
                    ][self.configuration.attr_id]
                    not in integrations_list
                ):
                    new_cfg_list.append(config_dict)
            except KeyError:
                new_cfg_list.append(config_dict)
                continue

        return self.__set_editable_cfg(new_cfg_list)

    def __editer_scripts_list(self, scripts_list: list[str]) -> list[str]:
        new_list = []

        for script_id in scripts_list:
            script_id = "script." + script_id
            new_list.append(script_id)
        return new_list

    def del_script_restore_state(self, scripts_list: list[str]) -> dict:
        editable_part = self.__get_editable_cfg()
        edit_scripts_list = self.__editer_scripts_list(scripts_list)
        new_cfg_list = []

        for config_dict in editable_part:
            if (
                config_dict[self.configuration.state][self.configuration.id_key]
                not in edit_scripts_list
            ):
                new_cfg_list.append(config_dict)

        return self.__set_editable_cfg(new_cfg_list)
