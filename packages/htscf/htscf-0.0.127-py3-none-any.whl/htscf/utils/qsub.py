import sys
import platform
from os.path import exists
from subprocess import Popen, PIPE
from datetime import datetime as dt


def qsub(nodes=1, cores=28, python_script=sys.argv[0]):
    """
    提交Python脚本作为PBS作业。
    :param python_script: 要执行的Python脚本路径。
    :param nodes: 请求的节点数，默认为1。
    :param cores: 每个节点请求的核数，默认为28。
    """
    QSUB_SCRIPT_PATH = "qsub.sh"
    LOG_FILE = "run.log"

    # 如果是Windows系统，直接返回
    if platform.system() == 'Windows':
        print("PBS job submission is not supported on Windows.")
        return

    # 如果PBS作业脚本不存在，则创建
    if not exists(QSUB_SCRIPT_PATH):
        scripts = f"""
#!/bin/bash
#PBS -N zh
#PBS -l nodes={nodes}:ppn={cores}
#PBS -q batch
#PBS -V
cd "${{PBS_O_WORKDIR}}" || exit
pwd >> hello
python "{python_script}"
""".strip()

        with open(QSUB_SCRIPT_PATH, "w") as sh:
            sh.write(scripts)

        # 提交作业
        process = Popen(f'qsub {QSUB_SCRIPT_PATH}', shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        info = stdout.decode("utf-8").strip()
        error = stderr.decode("utf-8").strip()

        # 打印作业提交结果
        print("任务ID:", info, "错误信息:", error)

        # 记录提交日志
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{dt.now()}: {info} {error}\n")
        with open(f"{dt.now()}", "w+") as fp:
            fp.write("hello")
        exit(0)
    else:
        with open(f"{dt.now()}", "w+") as fp:
            fp.write("hello")
        print("PBS作业脚本已存在，无需重复创建。请手动结束任务，以防止在主节点直接运算！由PBS调度请忽略该信息。")
