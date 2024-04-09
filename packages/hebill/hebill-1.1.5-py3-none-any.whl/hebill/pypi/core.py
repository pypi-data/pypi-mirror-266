import os.path
import subprocess
import hebill


class Pypi:
    def __init__(self):
        self._name = None
        self._version = None
        self._description = None
        self._long_description = None
        self._long_description_content_type = 'text/plain'
        self._packages = []
        self._install_requires = {}
        self._entry_point_console_scripts = {}
        self._python_requires = '3.12'
        self._output_build_base = ''
        self._output_dist_dir = ''
        self._output_egg_base = ''
        self._setup_py = 'setup_by_hebill.py'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version: str):
        self._version = version

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def packages(self):
        return self._packages

    def add_package(self, name: str):
        if name not in self._packages:
            self._packages.append(name)

    @property
    def long_description(self):
        return self._long_description

    @long_description.setter
    def long_description(self, file: str):
        self._long_description = file

    @property
    def long_description_content_type(self):
        return self._long_description_content_type

    def set_long_description_content_type_text(self):
        self._long_description_content_type = 'text/plain'

    def set_long_description_content_type_markdown(self):
        self._long_description_content_type = 'text/markdown'

    @property
    def install_requires(self):
        return self._install_requires

    def add_install_require(self, name: str, version: str):
        self._install_requires[name] = version

    @property
    def entry_point_console_scripts(self):
        return self._entry_point_console_scripts

    def add_entry_point_console_script(self, name: str, method: str):
        self._entry_point_console_scripts[name] = method

    @property
    def python_requires(self):
        return self._python_requires

    @python_requires.setter
    def python_requires(self, version: str):
        self._python_requires = version

    @property
    def output_build_base(self):
        return self._output_build_base

    @output_build_base.setter
    def output_build_base(self, path: str):
        self._output_build_base = path

    @property
    def output_dist_dir(self):
        return self._output_dist_dir

    @output_dist_dir.setter
    def output_dist_dir(self, path: str):
        self._output_dist_dir = path

    @property
    def output_egg_base(self):
        return self._output_egg_base

    @output_egg_base.setter
    def output_egg_base(self, path: str):
        self._output_egg_base = path

    @property
    def setup_py(self):
        return self._setup_py

    @setup_py.setter
    def setup_py(self, filename: str):
        self._setup_py = filename

    def clear(self):
        from ..dir.core import Dir
        Dir('build').delete()
        Dir('dist').delete()
        Dir(f'{self.name}.egg-info').delete()

    def build(self):
        self.clear()
        lines = [
            '# -*- coding: utf-8 -*-',
            'from setuptools import setup',
            'setup(',
            f'    name=\'{self.name if self.name else 'My Module'}\',',
            f'    version=\'{self.version if self.version else '1.0.0'}\',',
        ]
        if self.description:
            lines.append(f'{' ' * 4}description=\'{self.description}\',')
        if self.long_description:
            lines.append(f'{' ' * 4}long_description=open(r\'{os.path.abspath(self.long_description)}\').read(),')
            lines.append(f'{' ' * 4}long_description_content_type=\'{self.long_description_content_type}\',')
        lines.append(f'{' ' * 4}install_requires=[')
        if len(self.install_requires) > 0:
            for n, v in self.install_requires.items():
                lines.append(f'{' ' * 8}\'{n}=={v}\',')
        else:
            for i in hebill.file.File('requirements.txt').read_lines():
                if '~=' in i:
                    n, v = i.split('~=')
                    if n == 'setuptools':
                        continue
                    lines.append(f'{' ' * 8}\'{n}=={v}\',')
        lines.append(f'{' ' * 4}],')
        if len(self.entry_point_console_scripts) > 0:
            lines.append(f'{' ' * 4}entry_points={{')
            lines.append(f'{' ' * 8}\'console_scripts\':[')
            for n, v in self.entry_point_console_scripts.items():
                lines.append(f'{' ' * 12}\'{n} = {v}\':[')
            lines.append(f'{' ' * 8}],,')
            lines.append(f'{' ' * 4}}},')
        lines.append(f'{' ' * 4}python_requires=\'>={self.python_requires if self.python_requires else '3.12'}\',')
        """if self.output_build_base or self.output_dist_dir or self.output_egg_base:
            lines.append(f'{' '*4}options={{')
            if self.output_build_base:
                lines.append(f'{' '*8}\'build\': {{')
                lines.append(f'{' '*12}\'build\': r\'{self.output_build_base}\',')
                lines.append(f'{' '*8}}},')
            if self.output_dist_dir:
                lines.append(f'{' '*8}\'bdist_wheel\': {{')
                lines.append(f'{' '*12}\'dist_dir\': r\'{self.output_dist_dir}\',')
                lines.append(f'{' '*8}}},')
            if self.output_egg_base:
                lines.append(f'{' '*8}\'bdist_egg\': {{')
                lines.append(f'{' '*12}\'egg_base\': r\'{self.output_egg_base}\',')
                lines.append(f'{' '*8}}},')
            lines.append(f'{' '*4}}},')"""
        lines.append(')\n')
        try:
            with open(self.setup_py, 'w') as file:
                file.write('\n'.join(lines))
            print(f'{self.setup_py} 文件已经生成：{self.setup_py}')
        except (Exception, IOError) as e:
            print(f'{self.setup_py} 文件生成失败[{e}]')
            return

    def pack(self):
        self.build()
        command = [r'E:\PythonEnvs\hebill\Scripts\python.exe', self.setup_py, 'sdist', 'bdist_wheel']
        '''if self.output_build_base:
            command.extend(["--build-base", self.output_build_base])
        if self.output_dist_dir:
            command.extend(["--dist-dir", self.output_dist_dir])
        if self.output_egg_base:
            command.extend(["--egg-base", self.output_egg_base])'''
        print(f"执行命令：{' '.join(command)}")
        result = subprocess.run(' '.join(command))

        if result.returncode == 0:
            print("打包处理执行完成，下面开始上传")
        else:
            print("打包处理执行失败！")
            return
        command = ['twine', 'upload', 'dist/*']
        pypirc = hebill.dir.Dir(os.path.expanduser("~")).sub_file('.pypirc')
        if not pypirc.exists():
            print(f'没有查询到文件{pypirc.path}, 请手动上传：{' '.join(command)}')
        else:
            print(f"已找到认证文件{pypirc.path}，执行命令：{' '.join(command)}")
            process = subprocess.run(command, text=True, shell=True)

            if process.returncode == 0:
                print("上传成功")
                self.clear()
            else:
                print("上传失败！请检查错误信息，或手动上传：{' '.join(command)}")
                return
