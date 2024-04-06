class ScriptsEditor:
    def __init__(self, original_file: dict[str, any] | list[str]):
        self.edit_lines = None
        self.edit_file = None
        self.index_list = []
        self.original_file = original_file

    def change_file(self, new_file_part: dict[any]) -> dict:
        if isinstance(self.original_file, dict):
            self.original_file = self.original_file | new_file_part
            return self.original_file

    def delete_scripts(self, script_id: str) -> dict:
        self.edit_file = self.original_file
        if isinstance(self.original_file, dict):
            del self.edit_file[script_id]
        return self.edit_file

    def __delete_lines(self, index_list: list[int]):
        for index in index_list:
            del self.edit_lines[index]

    def __get_indexes(self, script_id) -> list[int]:
        comment_line = -1

        for line in self.edit_lines:
            if str(line) == str(script_id) + ":\n":
                if comment_line != -1 and "#" in self.edit_lines[comment_line]:

                    self.index_list.append(comment_line)
            comment_line += 1
        return self.index_list

    def delete_comments(self, script_id: str) -> list[str]:
        self.edit_lines = self.original_file
        self.__get_indexes(script_id)
        self.__delete_lines(self.index_list)
        return self.edit_lines
