import os

from HA_cfg_cleaner_DiosWolf.files_editors.fileIO_cls import FileIO


class FindInAllFiles:
    def __init__(self):
        self.path = [
            # r"C:\Users\wolkm\OneDrive\Робочий стіл\file_checker\save_folder\config",
            "/root/config",
            "/root/addon_configs",
            "/root/addons",
            "/root/backup",
            "/root/media",
            "/root/share",
            "/root/ssl",
        ]
        self.report_io = FileIO()

    def __get_catalogue(self) -> dict[str, list]:
        catalogue_dict = {}

        for scn_path in self.path:
            files = os.walk(scn_path)

            for path, _, files in files:
                catalogue_dict[path] = files

        return catalogue_dict

    def __find_file(
        self, file_lines: list[bytes], text_to_find: list[str]
    ) -> dict[str, list]:
        i = 0
        find_dict = {}
        for line in file_lines:

            i += 1
            for text in text_to_find:
                if text.encode(encoding="UTF-8") in line:

                    if text not in find_dict:
                        find_dict[text] = []
                        find_dict[text].append(i)

                    else:
                        find_dict[text].append(i)
        return find_dict

    def start_find(self, text_to_find: list[str]) -> dict[str, list]:
        catalogue = self.__get_catalogue()
        find_dict = {}

        for main_folder, files_dict in catalogue.items():
            for file in files_dict:

                file_path = main_folder + "/" + file

                find_dict[file_path] = []
                file_lines = self.report_io.read_with_type(
                    file_path, file_type="byte_lines"
                )
                new_dict = self.__find_file(file_lines, text_to_find)

                find_dict[file_path].append(new_dict)

        find_dict = dict(filter(lambda x: x[1][0], find_dict.items()))

        return find_dict
