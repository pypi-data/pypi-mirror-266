from argparse import ArgumentParser
from getpass import getpass
import requests as rq
import socket
import textwrap
from re import match
import json


class CLICommand:
    """删除pbs所有任务
    """

    @staticmethod
    def add_arguments(parser: ArgumentParser):
        pass

    @staticmethod
    def run(args, parser):
        from os import system
        from subprocess import Popen, PIPE

        popen = Popen("qstat", shell=True, stdout=PIPE)

        s = popen.stdout.read().decode("utf-8")
        data = s.split("\n")[2:-1]
        for i in data:
            print(i.split())
        data = list(map(lambda i: i.split()[0], data))
        for i in data:
            system(f"qdel {i}")
