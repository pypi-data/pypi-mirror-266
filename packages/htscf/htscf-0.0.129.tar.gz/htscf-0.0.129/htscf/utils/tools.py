import os
import re
import subprocess
import uuid
from functools import wraps
from hashlib import md5
from inspect import getattr_static
from io import StringIO
from os.path import join
from pathlib import Path
from re import Pattern, match
from shutil import copy
from subprocess import Popen, PIPE
from typing import List, Union, Iterator
from uuid import uuid4
from datetime import datetime
from ase import Atoms
from ase.io import read
from ase.io.cif import CIFBlock, parse_block
from ase.io.cif_unicode import format_unicode


def py2cmdline(script, args: list = None):
    if args is None:
        args = []
    args = map(lambda i: str(i), args)
    exs = 'exec(%r)' % re.sub('\r\n|\r', '\\n', script.rstrip())
    return 'python -c "%s"' % exs.replace('"', r'\"').replace("$", r"\$") + " " + " ".join(args)


def copyFile(src_dir, target_dir, file):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    src = join(src_dir, file)
    copy(src, target_dir)


def search(fp, target, exclude=None, recursion=False):
    """
    Search files.
    :param fp: file path.
    :param target: target filename or keywords.
    :param exclude: exclude filename or keywords.
    :param recursion: Whether to recursively search
    :return: a generator
    """
    abs_fp = os.path.abspath(fp)
    items = os.listdir(abs_fp)
    for item in items:
        item_fp = os.path.join(abs_fp, item)
        if os.path.isdir(item_fp) and recursion:
            for tmp in search(item_fp, target, exclude, recursion):
                yield tmp
        elif exclude:
            if target in item and exclude not in item:
                yield item_fp
        elif target in item:
            yield item_fp


def md5_hex(file: Union[str, Path]):
    """计算16进制的md5值
    """
    return md5(Path(file).read_bytes()).hexdigest()


def matchList(li: list, pattern: Union[str, Pattern], return_type="str"):
    """匹配列表中符合条件的第一列
    """
    for i in li:
        if match(pattern, i):
            if return_type == "str":
                return i
            elif return_type == "Match":
                return match(pattern, i)
    return ""


def matchManyList(li: list, patterns: List[Union[str, Pattern]]):
    return [matchList(li, pattern) for pattern in patterns]


def method_register(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        if getattr_static(cls, func.__name__, None):
            msg = 'Error method name REPEAT, {} has exist'.format(func.__name__)
            raise NameError(msg)
        else:
            setattr(cls, func.__name__, wrapper)
        return func

    return decorator


def parse_cif_ase(s) -> Iterator[CIFBlock]:
    """Parse a CIF file using ase CIF parser."""

    data = format_unicode(s)
    lines = [e for e in data.split('\n') if len(e) > 0]
    lines = [''] + lines[::-1]  # all lines (reversed)

    while lines:
        line = lines.pop().strip()
        if not line or line.startswith('#'):
            continue

        yield parse_block(lines, line)


def parse_cif_ase_string(s) -> Atoms:
    return list(parse_cif_ase(s))[0].get_atoms()


def cif2poscar(cif_content: str):
    sio = StringIO()
    atoms = parse_cif_ase_string(cif_content)
    atoms.write(sio, format="vasp")
    sio.seek(0)
    lines = sio.readlines()
    symbol = lines[5].split()
    number = lines[6].split()
    positions = lines[8:]
    d = {}
    for s, n in zip(symbol, number):
        n = int(n)
        if s not in d.keys():
            d.update({s: [0, []]})
        d[s][0] = d[s][0] + n
        d[s][1].extend([positions.pop(0) for _ in range(n)])
    _symbol = []
    _number = []
    _positions = []
    for k, v in d.items():
        _symbol.append(k)
        _number.append(str(v[0]))
        _positions.extend(v[1])
    name = "".join([f"{s}{n}" for s, n in zip(_symbol, _number)])
    content = f"{name}\n{''.join(lines[1:5])}{' ' + ' '.join(_symbol)}\n{'  ' + ' '.join(_number)}\n{lines[7]}{''.join(_positions)}"
    return content


def writeScript(rootPath: Path, script) -> Path:
    scriptFileName = f"script-{uuid4()}"  # 生成一个随机脚本名
    scriptPath = rootPath / scriptFileName
    scriptPath.write_text(script)
    return scriptPath.absolute()


def mpiRun(command: str, directory: Path, stdout_file="vasp.out", stderr_file="vasp.error") -> str:
    start_time = datetime.now()
    stdout_path = directory / stdout_file
    stderr_path = directory / stderr_file

    # 生成唯一的文件名后缀
    unique_suffix = uuid.uuid4()

    # 准备命令脚本
    mpi_commands = " && ".join([
        'NP=$(cat "$PBS_NODEFILE" | wc -l)',
        f'cat "$PBS_NODEFILE" | sort | uniq | tee /tmp/nodes.{unique_suffix} | wc -l',
        f'cat "$PBS_NODEFILE" > /tmp/nodefile.{unique_suffix}',
        f'mpirun -genv I_MPI_DEVICE ssm -machinefile /tmp/nodefile.{unique_suffix} -n "$NP" {command}',
        f'rm -rf /tmp/nodefile.{unique_suffix}',
        f'rm -rf /tmp/nodes.{unique_suffix}'
    ])

    with stdout_path.open('w') as stdout_file, stderr_path.open('w') as stderr_file:
        process = Popen(mpi_commands, cwd=directory, stdout=stdout_file, stderr=stderr_file, shell=True, executable='/bin/bash')
        process.wait()

    end_time = datetime.now()
    return (end_time - start_time).__str__()


def is_converge(filepath: Path) -> bool:
    """
    Checks if the calculation has converged based on the presence of a specific
    string in the OUTCAR file.

    Args:
        filepath (Path): The directory path where the OUTCAR file is located.

    Returns:
        bool: True if the calculation has converged, False otherwise.
    """
    outcar = filepath / "OUTCAR"
    try:
        with outcar.open() as fd:
            for line in fd:
                if "reached required accuracy" in line:
                    return True
        return False
    except FileNotFoundError:
        print(f"File {outcar} not found.")
        return False


def read_from_str(s: str, format_="cif") -> Atoms:
    """
    从字符串中读取结构到ase中
    例(从字符串读取vasp文件):
        atoms = read_from_str(
        "S12Al2P4Li2H4
1.0000000000000000
 6.8544000000000000    0.0000000000000000    0.0000000000000000
 0.0000000000000000   31.2483000000000004    0.0000000000000000
 0.0000000000000000    0.0000000000000000   18.0067999999999984
S Al P Li H
12 2 4 2 4
Cartesian
1.1436566399999999 19.2436405889999982  0.0682457720000000
4.5708566400000015 14.0357989110000005  0.0682457720000000
1.4675955839999999 15.8453879639999986  0.0000000000000000
5.3868044159999995 15.8453879639999986  3.0067754639999995",format="vasp")
    """
    with StringIO() as sio:
        sio.write(s)
        sio.seek(0)
        return read(sio, format=format_)


class Pipe:
    def __init__(self, command, current_directory, encoding="utf-8"):
        self.command = command
        self.current_directory = current_directory
        self.encoding = encoding
        self.stdout = ""
        self.stderr = ""
        self.pipe()

    def pipe(self):
        popen = Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                      cwd=self.current_directory)
        stdout, stderr = popen.communicate()
        if stdout:
            self.stdout = stdout.decode(self.encoding)
            return
        if stderr:
            self.stderr = stderr.decode(self.encoding)


def execute_command(command, shell=False):
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=shell, text=True) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {process.returncode}")
        return stdout, stderr


def del_nested_attr(obj, attr):
    """
    尝试删除一个嵌套属性，如果成功删除则返回 True，否则返回 False。

    :param obj: 目标对象或字典
    :param attr: 属性的路径，例如 "step_details.file"
    :return: 布尔值，表示属性是否被成功删除
    """
    # 分割属性路径
    parts = attr.split('.')

    # 遍历到最后一个属性之前的路径
    for part in parts[:-1]:
        if not isinstance(obj, dict) or part not in obj:
            return False
        obj = obj[part]

    # 删除最终的属性
    if isinstance(obj, dict) and parts[-1] in obj:
        del obj[parts[-1]]
        return True
    else:
        return False
