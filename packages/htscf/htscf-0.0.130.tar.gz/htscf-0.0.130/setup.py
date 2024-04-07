from setuptools import setup

with open(r"C:\Users\ZH\Desktop\important\hse_process\htsct-package\requirements.txt") as fd:
    requires = fd.read().split("\n")
setup(
    install_requires=requires
)
