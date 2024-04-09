import os


class Dir(str):
    def __init__(self, path: str):
        self._input = path

    @property
    def path(self) -> str:
        return os.path.abspath(self._input)

    @property
    def name(self) -> str:
        return os.path.basename(self._input)

    @property
    def parent(self):
        return Dir(self.parent_path)

    @property
    def parent_path(self) -> str:
        return os.path.abspath(os.path.dirname(self.path))

    @property
    def parent_name(self) -> str:
        return os.path.basename(os.path.dirname(self.path))

    def exists(self):
        return os.path.isdir(self.path)

    def sub_file(self, name: str):
        from ..file.core import File
        return File(os.path.join(self.path, name))

    def sub_dir(self, name: str):
        return Dir(os.path.join(self.path, name))

    def list_sub_names(self):
        if self.exists():
            return os.listdir(self.path)
        return []

    def list_sub_paths(self):
        r = []
        for i in self.list_sub_names():
            r.append(os.path.join(self.path, i))
        return r

    def list_sub_file_names(self) -> list:
        r = []
        for i in self.list_sub_names():
            if os.path.isfile(os.path.join(self.path, i)):
                r.append(i)
        return r

    def list_sub_file_paths(self) -> list:
        r = []
        for i in self.list_sub_paths():
            if os.path.isfile(i):
                r.append(i)
        return r

    def list_sub_dir_names(self) -> list:
        r = []
        for i in self.list_sub_names():
            if os.path.isdir(os.path.join(self.path, i)):
                r.append(i)
        return r

    def list_sub_dir_paths(self) -> list:
        r = []
        for i in self.list_sub_paths():
            if os.path.isdir(i):
                r.append(i)
        return r

    def delete(self):
        if self.exists():
            for i in self.list_sub_file_paths():
                from ..file.core import File
                File(i).delete()
            for i in self.list_sub_dir_paths():
                Dir(i).delete()
            os.rmdir(self.path)
