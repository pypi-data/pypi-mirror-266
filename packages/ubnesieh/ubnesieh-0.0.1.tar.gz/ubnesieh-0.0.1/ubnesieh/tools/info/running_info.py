import sys
from pathlib import Path


class RunningInfo(object):

    @property
    def __work_path(self):
        cur_file = sys.argv[0]
        path = Path(cur_file)
        return path

    def mk_subdir_for_current_directory(self, subdir='cache'):
        _dir = self.current_directory
        path = Path(_dir) / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def work_directory(self):
        return self.current_directory

    @property
    def current_directory(self):
        path = self.__work_path
        cur_dir = path.resolve().parent
        return cur_dir

    @property
    def current_file_name(self):
        path = self.__work_path
        file_name = path.stem
        return file_name

    @property
    def current_file_name_with_extension(self):
        path = self.__work_path
        file_name, extension = path.stem, path.suffix
        return file_name, extension
