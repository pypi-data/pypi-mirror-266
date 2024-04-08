# coding: utf-8

import os.path
import time
from FileSystemModel._dir import Dir
from FileSystemModel._file import File


class Path:
    _date_fmt: str = '%Y/%m/%d %H:%M:%S'
    _field_names: tuple[str] = ('ID', 'Basename', 'Owner', 'Size', 'Type', 'Creation Time', 'Modification Time',
                                'Readable', 'Writable', 'Executable')
    _size_units: tuple[str] = 'GB', 'MB', 'KB', 'B'
    _size_levels: tuple[int] = 1024 * 1024 * 1024, 1024 * 1024, 1024, 0
    _RIGHT: str = 'r'
    _LEFT: str = 'l'
    _DIR_TYPE: str = '<DIR>'
    _FILE_TYPE: str = '<FILE>'

    def __init__(self, path: str):
        self.path: str = path
        self.dirs: list[Dir] = []
        self.files: list[File] = []
        self.change_path(self.path)

    def __str__(self):
        dirs = ''.join(str(dir_) + '\n' for dir_ in self.dirs)
        files = ''.join(str(file) + '\n' for file in self.files)
        return dirs + files

    def _strfsize(self, size: int):
        for index, level in enumerate(self._size_levels):
            if size >= level:
                if level != 0:
                    size /= level
                return f'{size:.2f} {self._size_units[index]:>2s}'
        return ''

    def _strftime(self, timestamp: int):
        if timestamp < 0:
            return ''
        t: time.struct_time = time.localtime(timestamp)
        return time.strftime(self._date_fmt, t)

    def change_path(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f'[WinError 3] The system cannot find the path specified.: {path!r}')
        if not os.path.isdir(path):
            raise NotADirectoryError(f'[WinError 267] The directory name is invalid.: {path!r}')
        self.path = path
        self.dirs.clear()
        self.files.clear()
        for file in os.listdir(self.path):
            file = os.path.join(self.path, file)
            if os.path.isdir(file):
                self.dirs.append(Dir(file))
            elif os.path.isfile(file):
                self.files.append(File(file))

    def cd(self, path: str):
        self.change_path(os.path.split(self.path)[0] if path == '..' else os.path.join(self.path, path))
