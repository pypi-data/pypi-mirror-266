import sys
from argparse import ArgumentParser

from PySide2.QtWidgets import QApplication

from htscf.gui.RibbonBuilder import MainWindow


class CLICommand:
    """Ribbon Builder
    """

    @staticmethod
    def add_arguments(parser: ArgumentParser):
        pass

    @staticmethod
    def run(args, parser):
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
