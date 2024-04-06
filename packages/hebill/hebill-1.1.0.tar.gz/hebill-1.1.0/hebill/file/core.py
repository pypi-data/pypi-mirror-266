import os
import psutil


class File:
    def __init__(self, file: str):
        self._file = file

    @property
    def file(self) -> str: return self._file

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
    def absolute_path(self) -> str: return os.path.abspath(self._file)

    @property
    def basename(self) -> str: return os.path.basename(self._file)

    def is_occupied(self):
        for proc in psutil.process_iter():
            try:
                files = proc.open_files()  # 获取进程打开的文件列表
                for f in files:  # 检查文件路径是否匹配
                    if f.path == self.absolute_path:  # 文件被锁定
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
