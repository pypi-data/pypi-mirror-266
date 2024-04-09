# coding: utf-8

from anacondas.FileSystemModel._dir import Dir
from anacondas.FileSystemModel._file import File
from anacondas.FileSystemModel._path import Path
from prettytable import PrettyTable
from typing import Literal
from typing import Optional


class FileSystemModel(Path):

    def __init__(self, path: str):
        super().__init__(path)

    def show(self, kind: Optional[Literal['all', 'dir', 'file']] = None, title: bool = True,
             owner: bool = True, size: bool = True, ctime: bool = True, mtime: bool = True,
             readable: bool = True, writable: bool = True, executable: bool = True):
        table = PrettyTable(self._field_names, title=self.path)
        table.align['ID'] = self._RIGHT
        table.align['Basename'] = self._LEFT
        table.align['Owner'] = self._LEFT
        table.align['Size'] = self._RIGHT
        if kind is None or kind == 'all' or kind == 'dir':
            table.add_rows((id_, dir_.name, dir_.owner, self._strfsize(-1), self._DIR_TYPE,
                            self._strftime(dir_.ctime), self._strftime(dir_.mtime),
                            dir_.readable, dir_.writable, dir_.executable)
                           for id_, dir_ in enumerate(self.dirs))
        if kind is None or kind == 'all' or kind == 'file':
            table.add_rows((id_, file.name, file.owner, self._strfsize(file.size), self._FILE_TYPE,
                            self._strftime(file.ctime), self._strftime(file.mtime),
                            file.readable, file.writable, file.executable)
                           for id_, file in enumerate(self.files, len(self.dirs)))
        if title is False:
            table.title = ''
        if owner is False:
            table.del_column('Owner')
        if size is False:
            table.del_column('Size')
        if ctime is False:
            table.del_column('Creation Time')
        if mtime is False:
            table.del_column('Modification Time')
        if readable is False:
            table.del_column('Readable')
        if writable is False:
            table.del_column('Writable')
        if executable is False:
            table.del_column('Executable')
        print(table)
