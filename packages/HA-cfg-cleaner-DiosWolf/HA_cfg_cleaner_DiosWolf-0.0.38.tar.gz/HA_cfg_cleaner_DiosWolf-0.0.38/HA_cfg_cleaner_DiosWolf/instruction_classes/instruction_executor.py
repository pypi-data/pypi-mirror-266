import logging

from HA_cfg_cleaner_DiosWolf.castom_errors.castom_errors import (
    CustomError,
    CustomError,
)
from HA_cfg_cleaner_DiosWolf.data_classes_json.file_config import ConfigurationFile
from HA_cfg_cleaner_DiosWolf.data_classes_json.instructions import (
    Instructions,
    ChangeAddonsOptions,
)
from HA_cfg_cleaner_DiosWolf.files_editors.addons_editor import AddonsEditor
from HA_cfg_cleaner_DiosWolf.files_editors.automations_editor import AutomationsEditor
from HA_cfg_cleaner_DiosWolf.files_editors.editor_restore_state import EditorRestoreFile
from HA_cfg_cleaner_DiosWolf.files_editors.fileIO_cls import FileIO
from HA_cfg_cleaner_DiosWolf.files_editors.file_folder_editor_cls import (
    FileFoldersEditor,
)
from HA_cfg_cleaner_DiosWolf.files_editors.find_in_files_cls import FindInAllFiles
from HA_cfg_cleaner_DiosWolf.files_editors.integrations_cls import IntegrationsEditor
from HA_cfg_cleaner_DiosWolf.files_editors.script_editor_cls import ScriptsEditor

logging.basicConfig(
    level=logging.DEBUG,
    filename="./config/script_logs.log",
    filemode="w",
    format="\n%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


class InstructionsExecute:
    def __init__(
        self,
        all_instructions: Instructions,
        file_io: FileIO,
        all_configs: ConfigurationFile,
    ):
        self.all_instructions = all_instructions
        self.all_configs = all_configs
        self.file_io = file_io

    def del_integrations(self):
        ids_list: list[str] = self.all_instructions.delete_integrations.ids_list
        for configuration in self.all_configs.configurations:
            full_cfg = self.file_io.read_with_type(
                configuration.path + configuration.filename, configuration.type_cfg
            )
            integration_editor = IntegrationsEditor(configuration, full_cfg)

            try:
                new_cgf = integration_editor.delete_integration(ids_list)
                self.file_io.write_with_type(
                    configuration.path + configuration.filename,
                    new_cgf,
                    configuration.type_cfg,
                )
            except Exception as e:
                print("Error, check log file")
                logging.error("Exception", exc_info=True)

    def enable_integrations(self):
        ids_list: list[str] = self.all_instructions.enable_integration.ids_list

        for configuration in self.all_configs.configurations:
            full_cfg = self.file_io.read_with_type(
                configuration.path + configuration.filename, configuration.type_cfg
            )
            integration_editor = IntegrationsEditor(configuration, full_cfg)
            new_cgf = integration_editor.disable_enable_integration(
                ids_list, configuration.on_integration
            )
            self.file_io.write_with_type(
                configuration.path + configuration.filename,
                new_cgf,
                configuration.type_cfg,
            )

    def disable_integrations(self):
        ids_list: list[str] = self.all_instructions.disable_integration.ids_list

        for configuration in self.all_configs.configurations:
            full_cfg = self.file_io.read_with_type(
                configuration.path + configuration.filename, configuration.type_cfg
            )
            integration_editor = IntegrationsEditor(configuration, full_cfg)

            new_cgf = integration_editor.disable_enable_integration(
                ids_list, configuration.off_integration
            )
            self.file_io.write_with_type(
                configuration.path + configuration.filename,
                new_cgf,
                configuration.type_cfg,
            )

    def del_automations(self):
        ids_list: list[str] = self.all_instructions.delete_automations.ids_list

        for configuration in self.all_configs.automations_cfg:

            full_cfg = self.file_io.read_with_type(
                configuration.path + configuration.filename, configuration.type_cfg
            )

            try:
                automation_editor = AutomationsEditor(configuration, full_cfg)
                new_cgf = automation_editor.delete_automation(ids_list)

                self.file_io.write_with_type(
                    configuration.path + configuration.filename,
                    new_cgf,
                    configuration.type_cfg,
                )
            except Exception as e:
                print("Error, check log file")
                logging.error("Exception", exc_info=True)

    def del_automations_restore_state(self):
        ids_list: list[str] = self.all_instructions.delete_automations.ids_list
        full_cfg = self.file_io.read_with_type(
            self.all_configs.config_restore_state.path
            + self.all_configs.config_restore_state.filename,
            self.all_configs.config_restore_state.type_cfg,
        )

        automation_editor = EditorRestoreFile(
            self.all_configs.config_restore_state, full_cfg
        )
        new_cgf = automation_editor.del_automation_restore_state(ids_list)

        self.file_io.write_with_type(
            self.all_configs.config_restore_state.path
            + self.all_configs.config_restore_state.filename,
            new_cgf,
            self.all_configs.config_restore_state.type_cfg,
        )

    def disable_automations(self):
        ids_list: list[str] = self.all_instructions.disable_automations.ids_list
        for configuration in self.all_configs.automations_cfg:

            if configuration.config_id == "entity_registry":
                full_cfg = self.file_io.read_with_type(
                    configuration.path + configuration.filename, configuration.type_cfg
                )

                self.all_configs.host_info.api_key = (
                    self.all_instructions.disable_automations.host_info.api_key
                )

                if self.all_instructions.disable_automations.host_info.host is not None:

                    self.all_configs.host_info.host = (
                        self.all_instructions.disable_automations.host_info.host
                    )
                    self.all_configs.host_info.port = (
                        self.all_instructions.disable_automations.host_info.port
                    )

                automation_editor = AutomationsEditor(
                    configuration, full_cfg, self.all_configs.host_info
                )
                try:
                    automation_editor.disable_automation(ids_list)

                except CustomError as error:
                    print(f"Error, check log file\n{error.error_text}")
                    logging.error(f"Exception {error.error_text}", exc_info=True)
                    break

                except Exception as e:
                    print("Error, check log file")
                    logging.error("Exception", exc_info=True)

    def del_addons(self):
        ids_list: list[str] = self.all_instructions.delete_addons.ids_list
        for addon_id in ids_list:
            try:
                addon_editor = AddonsEditor(self.all_configs.ssh_commands)
                addon_editor.use_ssh_addon(
                    addon_id, self.all_configs.ssh_commands.delete_addons
                )
            except CustomError as e:
                print("Error, check log file")
                logging.error(f"Exception {addon_id} {e.error_text}")

    def disable_addons(self):
        ids_list: list[str] = self.all_instructions.disable_addons.ids_list
        for addon_id in ids_list:
            try:
                addon_editor = AddonsEditor(
                    self.all_configs.ssh_commands, self.all_configs.host_info
                )
                addon_editor.stop_autoboot(addon_id)

                addon_editor = AddonsEditor(self.all_configs.ssh_commands)
                addon_editor.use_ssh_addon(
                    addon_id, self.all_configs.ssh_commands.disable_addons
                )

            except Exception as e:
                print("Error, check log file")
                logging.error(f"Exception {addon_id} {e}", exc_info=True)

    def change_addons_options(self):
        addons_dict: list[ChangeAddonsOptions] = (
            self.all_instructions.change_addons_options
        )
        for addon_dict in addons_dict:

            try:
                addon_editor = AddonsEditor(
                    self.all_configs.ssh_commands, self.all_configs.host_info
                )
                addon_editor.change_addon_options(
                    addon_dict.addon_id, addon_dict.addon_options
                )

            except Exception as e:
                print("Error, check log file")
                logging.error("Exception", exc_info=True)

    def del_script_comments(self):
        for instruction in self.all_instructions.delete_script:
            file_lines = self.file_io.read_with_type(
                instruction.path, file_type="all_lines"
            )
            script_editor = ScriptsEditor(file_lines)

            for script_id in instruction.scripts_ids:
                script_editor.delete_comments(script_id)

            self.file_io.write_with_type(
                instruction.path, script_editor.edit_lines, file_type="all_lines"
            )

    def del_script(self):
        for instruction in self.all_instructions.delete_script:

            full_cfg = self.file_io.read_with_type(instruction.path)
            script_editor = ScriptsEditor(full_cfg)

            for script_id in instruction.scripts_ids:
                try:
                    script_editor.delete_scripts(script_id)

                except KeyError:
                    logging.error(
                        f"Can't find script id {script_id} in {instruction.path}"
                    )

                except Exception as e:
                    logging.error(f"Error: {e}")

            self.file_io.write_with_type(instruction.path, script_editor.edit_file)

    def del_script_restore_state(self):
        restore_path = (
            self.all_configs.config_restore_state.path
            + self.all_configs.config_restore_state.filename
        )
        full_cfg = self.file_io.read_with_type(
            restore_path, self.all_configs.config_restore_state.type_cfg
        )
        restore_script = EditorRestoreFile(
            self.all_configs.config_restore_state, full_cfg
        )

        for instruction in self.all_instructions.delete_script:

            try:
                restore_script.del_script_restore_state(instruction.scripts_ids)

            except Exception as e:
                print("Error, check log file")
                logging.error("Exception", exc_info=True)

        self.file_io.write_with_type(
            restore_path,
            restore_script.full_cfg,
            self.all_configs.config_restore_state.type_cfg,
        )

    def del_objects(self):
        fl_fld_editor = FileFoldersEditor()
        for delete_object in self.all_instructions.delete_objects:
            for object_name in delete_object.objects_names:
                path = delete_object.path + "/" + object_name
                try:
                    fl_fld_editor.delete_objects(path)
                except Exception as e:
                    print("Error, check log file")
                    logging.error("Exception", exc_info=True)

    def clean_folders(self):
        fl_fld_editor = FileFoldersEditor()
        for delete_object in self.all_instructions.clean_folders:
            for object_name in delete_object.folders_names:
                path = delete_object.path + "/" + object_name
                try:
                    fl_fld_editor.clean_folders(path)
                except Exception as e:
                    print("Error, check log file")
                    logging.error("Exception", exc_info=True)

    def clean_files(self):
        fl_fld_editor = FileFoldersEditor()
        for delete_object in self.all_instructions.clean_files:
            for object_name in delete_object.files_names:
                path = delete_object.path + "/" + object_name
                try:
                    fl_fld_editor.clean_files(path)
                except Exception as e:
                    print("Error, check log file")
                    logging.error("Exception", exc_info=True)

    def change_files(self):
        for file_info in self.all_instructions.change_files:
            try:
                orig_file = self.file_io.read_with_type(file_info.path)
                file_editor = ScriptsEditor(orig_file)
                for new_part in file_info.new_content:
                    file_editor.change_file(new_part)
                self.file_io.write_with_type(file_info.path, file_editor.original_file)
            except Exception as e:
                print("Error, check log file")
                logging.error("Exception", exc_info=True)

    def searching_in_files(self):
        if self.all_instructions.find_in_all_files.report_path:

            searcher = FindInAllFiles()
            find_dict = searcher.start_find(
                self.all_instructions.find_in_all_files.text_to_find
            )

            try:
                self.file_io.json_write(
                    self.all_instructions.find_in_all_files.report_path, find_dict
                )
            except FileNotFoundError:
                print("Error, check log file")
                logging.error(
                    f"Can't find path {self.all_instructions.find_in_all_files.report_path} for create result file"
                )
