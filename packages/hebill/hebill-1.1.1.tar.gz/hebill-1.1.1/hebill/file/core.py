import os
from ..dir.core import Dir


class File(str):
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

    def exists(self): return os.path.isfile(self.path)

    def _read_file(self):
        try:
            with open(self.absolute_path, 'r') as file:
                result = []
                lines = file.readlines()
                for line in lines:
                    result.append(line.replace('\n', ''))
                return result
        except (FileNotFoundError, Exception):
            pass
        return []

    def read_content(self):
        return '\n'.join(self._read_file())

    def read_lines(self):
        return self._read_file()

    @property
    def absolute_path(self) -> str: return os.path.abspath(self.path)

    @property
    def basename(self) -> str: return os.path.basename(self.path)

    def is_occupied(self):
        import psutil
        for proc in psutil.process_iter():
            try:
                files = proc.open_files()  # 获取进程打开的文件列表
                for f in files:  # 检查文件路径是否匹配
                    if f.path == self.absolute_path:  # 文件被锁定
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def delete(self):
        if self.exists():
            os.remove(self.absolute_path)
