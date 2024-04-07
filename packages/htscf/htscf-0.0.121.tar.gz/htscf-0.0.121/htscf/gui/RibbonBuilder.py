import os
import sys
import webbrowser
from itertools import chain
from pathlib import Path

import PySide2
import toml
import yaml
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from htscf.gui.UI_BuildRibbon import Ui_MainWindow
from htscf.gui._ase import GUIProcess, ASEGUI
from htscf.utils.tools import parse_cif_ase_string
from htscf.gui.defaultConfig import ui_config

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


class MainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.tasks = []
        self.data = {}
        self.state = {"subGUIState": False}
        self.guiConfig = {}
        self.setupUi(self)
        self.loadUIConfig()

    def blockAllSignal(self, flag):
        for obj in self.findChildren(QObject):
            obj.blockSignals(flag)

    def loadUIConfig(self):
        self.blockAllSignal(True)
        for k, v in ui_config.items():
            className = v["className"]
            data = v["data"]
            if className == "QLineEdit":
                getattr(self, k).setText(str(data))
            if className == "QComboBox":
                getattr(self, k).addItems(data)
                getattr(self, k).setCurrentIndex(v["currentIndex"])
            if className == "QCheckBox":
                getattr(self, k).setChecked(data)
        self.loadStructuresSlot()
        self.blockAllSignal(False)

    def configCollection(self):
        children = self.findChildren(QObject)
        for child in children:
            className = child.__class__.__name__
            objName = child.objectName()
            # 提取公共数据
            if className in ("QLineEdit", "QComboBox", "QCheckBox"):
                self.guiConfig.update({objName: {"className": className}})
            # 提出特殊数据
            if className == "QLineEdit":
                self.guiConfig[objName].update({"data": child.text()})
            if className == "QComboBox":
                data = [child.itemText(i) for i in range(child.count())]
                self.guiConfig[objName].update({"data": data, "currentIndex": child.currentIndex()})
            if className == "QCheckBox":
                self.guiConfig[objName].update({"data": 1 if child.isChecked() else 0})

    @staticmethod
    def changeComboboxByText(comboBoxObj, text):
        index = comboBoxObj.findText(text)
        comboBoxObj.setCurrentIndex(index if index >= 0 else 0)

    def saveGuiConfig(self):
        self.configCollection()
        with open("./config.toml", "w+") as fd:
            toml.dump(self.guiConfig, fd)

    def closeEvent(self, a0):
        self.saveGuiConfig()
        super(MainWindow, self).closeEvent(a0)

    @property
    def filePath(self):
        return Path(self.rootPath.text()) / self.choiceStructure.currentText()

    def openFilesSlot(self):
        obj = self.sender()
        objName = obj.objectName()
        if objName in ("openRootPath", "actionOpen"):
            fileDialog = QFileDialog(self, directory=".")
            fileDirectory = fileDialog.getExistingDirectory(self, "选择根目录...")
            if fileDirectory:
                self.rootPath.setText(Path(fileDirectory).__str__())
        if objName == "backRootPath":
            path = Path(self.rootPath.text())
            self.rootPath.setText(path.parent.__str__())
        if objName == "openSavePath":
            fileDialog = QFileDialog(self, directory=".")
            fileDirectory = fileDialog.getExistingDirectory(self, "选择保存目录...")
            if fileDirectory:
                self.savedPath.setText(Path(fileDirectory).__str__())

    def loadStructuresSlot(self):
        self.choiceStructure.clear()
        filePath = Path(self.rootPath.text())
        cifs = [i.name for i in chain(filePath.glob("*.cif"), filePath.glob("*.yacif"))]
        cifs.sort(key=lambda x: int(x.split(".", maxsplit=1)[0]))
        self.choiceStructure.addItems(cifs)

    def nextStructureSlot(self):
        count = self.choiceStructure.count()
        newIndex = self.choiceStructure.currentIndex() + 1
        if count:
            self.choiceStructure.setCurrentIndex(newIndex if newIndex < count else 1)

    def parseStructureSlot(self, *args):
        """由self.choiceStructure状态改变调用
        """
        suffix = self.filePath.suffix
        if suffix == ".cif":
            self.data["cif"] = self.filePath.read_text(encoding="utf-8")
            self.data["structureInfo"] = {}
        if suffix == ".yacif":
            with open(self.filePath, encoding="utf-8") as fd:
                data = yaml.load(fd, Loader=yaml.FullLoader)
            if data:
                self.data.update(data)

    def saveToPathSlot(self):
        savePath = Path(self.savedPath.text()) / "save"
        savePath.mkdir(parents=True, exist_ok=True)
        if self.filePath.is_file():
            saveFilePath = savePath / (self.filePath.name.rsplit(".", maxsplit=1)[0] + ".yacif")
            self.configCollection()
            with saveFilePath.open(mode="w+", encoding="utf-8") as fd:
                yaml.dump(
                    {"cif": self.data["cif"], "guiConfig": self.guiConfig, "structureInfo": self.data["structureInfo"]},
                    fd)

    def changeComboBoxSlot(self):
        obj = self.sender()
        objName = obj.objectName()
        if objName == "toggleVectorAB":
            vectorA = self.vectorA.currentText()
            vectorB = self.vectorB.currentText()
            self.changeComboboxByText(self.vectorA, vectorB)
            self.changeComboboxByText(self.vectorB, vectorA)
        if objName == "setVector1_2":
            self.changeComboboxByText(self.widthControlBase, "1")
            self.changeComboboxByText(self.widthControlDelta, "2")
        if objName == "setVector2_2":
            self.changeComboboxByText(self.widthControlBase, "2")
            self.changeComboboxByText(self.widthControlDelta, "2")
        if objName == "setVector2_3":
            self.changeComboboxByText(self.widthControlBase, "2")
            self.changeComboboxByText(self.widthControlDelta, "3")
        if objName == "setVectorZigzag":
            self.changeComboboxByText(self.vectorA, "1,1,0")
            self.changeComboboxByText(self.vectorB, "1,-1,0")
        if objName == "setVectorArmchair":
            self.changeComboboxByText(self.vectorA, "1,-1,0")
            self.changeComboboxByText(self.vectorB, "1,1,0")
        if objName == "setVectorHorizontal":
            self.changeComboboxByText(self.vectorA, "1,0,0")
            self.changeComboboxByText(self.vectorB, "0,1,0")
        if objName == "setVectorVertical":
            self.changeComboboxByText(self.vectorA, "0,1,0")
            self.changeComboboxByText(self.vectorB, "1,0,0")

    def taskHandlerSlot(self):
        obj = self.sender()
        objName = obj.objectName()
        if objName == "runProgram":
            self.configCollection()
            task = GUIProcess(self.guiConfig)
            task.start()
            self.tasks.append(task)
        if objName == "stopProgram":
            for task in self.tasks:
                task.terminate()

    def showStructureSlot(self):
        subGUIState = self.state["subGUIState"]
        if self.filePath.is_file():
            if subGUIState:
                self.ase_gui.close()
                self.state["subGUIState"] = False
            else:
                self.state["subGUIState"] = True
                if self.filePath.suffix == ".yacif":
                    atoms = parse_cif_ase_string(self.data["cif"])
                else:
                    atoms = self.filePath
                self.ase_gui = ASEGUI(self, atoms,
                                      repeat_images=
                                      (
                                          int(self.repeatA.text()),
                                          int(self.repeatB.text()),
                                          int(self.repeatC.text()))
                                      )
                self.ase_gui.show()

    def changeShowStructureSlot(self):
        if self.state["subGUIState"]:
            self.ase_gui.close()
            self.state["subGUIState"] = False
        self.showStructureSlot()

    def getHelp(self):
        webbrowser.open("https://zhaohao-cloud.gitee.io")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
