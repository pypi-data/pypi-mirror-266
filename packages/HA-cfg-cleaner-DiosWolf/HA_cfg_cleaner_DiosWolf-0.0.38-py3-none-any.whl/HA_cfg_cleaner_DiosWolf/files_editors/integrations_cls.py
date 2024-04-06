from HA_cfg_cleaner_DiosWolf.data_classes_json.file_config import Configuration


class IntegrationsEditor:

    def __init__(self, configuration: Configuration, full_cfg: dict):
        self.configuration = configuration
        self.full_cfg = full_cfg

    def __get_editable_cfg(self) -> dict:
        if self.configuration.first_key is None:
            return self.full_cfg

        elif self.configuration.second_key is None:
            return self.full_cfg[self.configuration.first_key]

        else:
            return self.full_cfg[self.configuration.first_key][
                self.configuration.second_key
            ]

    def __set_editable_cfg(self, edit_cfg_part: list[dict]) -> list[dict] | dict:

        if self.configuration.first_key is None:
            self.full_cfg = edit_cfg_part

        elif self.configuration.second_key is None:
            self.full_cfg: dict
            self.full_cfg[self.configuration.first_key] = edit_cfg_part

        else:
            self.full_cfg: dict
            self.full_cfg[self.configuration.first_key][
                self.configuration.second_key
            ] = edit_cfg_part

        return self.full_cfg

    def disable_enable_integration(
        self, integrations_list: list[str], on_off_flag: str | None
    ) -> list[dict]:
        editable_part = self.__get_editable_cfg()
        new_cfg_list = []

        for config_dict in editable_part:

            if isinstance(config_dict[self.configuration.identifiers_key], list):

                for ident in config_dict[self.configuration.identifiers_key]:
                    for del_device in ident:

                        if del_device in integrations_list:
                            config_dict[self.configuration.on_off_field] = on_off_flag

            else:
                if config_dict[self.configuration.identifiers_key] in integrations_list:
                    config_dict[self.configuration.on_off_field] = on_off_flag

            new_cfg_list.append(config_dict)

        return self.__set_editable_cfg(new_cfg_list)

    def delete_integration(self, integrations_list: list[str]) -> list[dict]:
        editable_part = self.__get_editable_cfg()
        new_cfg_list = []
        add_in_list = True

        for config_dict in editable_part:

            if isinstance(config_dict[self.configuration.identifiers_key], list):
                for ident in config_dict[self.configuration.identifiers_key]:
                    add_in_list = True

                    for del_device in ident:
                        if del_device in integrations_list:
                            add_in_list = False

                if add_in_list:
                    new_cfg_list.append(config_dict)

            else:
                if (
                    config_dict[self.configuration.identifiers_key]
                    not in integrations_list
                ):
                    new_cfg_list.append(config_dict)

        return self.__set_editable_cfg(new_cfg_list)
