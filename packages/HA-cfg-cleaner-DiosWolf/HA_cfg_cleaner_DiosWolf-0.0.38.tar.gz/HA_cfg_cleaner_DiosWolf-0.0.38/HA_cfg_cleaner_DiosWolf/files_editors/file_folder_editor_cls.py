import os
import shutil


class FileFoldersEditor:
    def delete_objects(self, path: str):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def clean_folders(self, folder_path: str):
        shutil.rmtree(folder_path)
        os.mkdir(folder_path)

    def clean_files(self, path: str):
        with open(path, "wb") as _:
            pass
