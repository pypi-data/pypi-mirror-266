from copy import deepcopy
from io import BytesIO
from multiprocessing import Process
from pathlib import PurePath, Path
from typing import IO
from typing import Union

import yaml
from ase.gui.gui import GUI
from ase.io import read
from ase.io.cif import parse_cif_ase

from htsct.core.buildRibbon import RibbonBuilder
from htsct.utils.tools import md5_hex, parse_cif_ase_string

NameOrFile = Union[str, PurePath, IO]


class ASEGUI(GUI):
    def __init__(self, parent=None, atoms=None, repeat_images=(3, 1, 1), *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(atoms, (str, PurePath, IO)):
            atoms = read(atoms)
        self.parent = parent
        self.new_atoms(atoms)
        self.images.repeat_images(repeat_images)
        self.set_frame()
        self.toggle_show_bonds(self)

    def show(self):
        if self.parent:
            self.parent.showStructure.setText("Close")
        self.run()

    def close(self):
        self.exit()

    def exit(self, event=None):
        super().exit(event)
        if self.parent:
            self.parent.showStructure.setText("Show")
            self.parent.state["subGUIState"] = False
            del self.parent.ase_gui
            self.parent.ase_gui = None


class GUIProcess(Process):
    def __init__(self, guiConfig, *args, **kwargs):
        super(GUIProcess, self).__init__(*args, **kwargs)
        self.guiConfig = guiConfig
        for k, v in guiConfig.items():
            if "currentIndex" in v.keys():
                d = v["data"][v["currentIndex"]]
            else:
                d = v["data"]
            setattr(self, k, d)
        self.repeatImages = (int(self.repeatA), int(self.repeatB), int(self.repeatC))
        self.filePath = Path(self.rootPath) / self.choiceStructure
        self.connectivity = (float(self.connectivityMin), float(self.connectivityMax))
        self.bottom = int(self.bottom)
        self.top = int(self.top)
        self.widthControlBase = int(self.widthControlBase)
        self.widthControlDelta = int(self.widthControlDelta)
        self.widthControlOrigo = int(self.widthControlOrigo)
        self.milerIndex = (
            list(map(lambda x: int(x), self.vectorA.split(","))),
            list(map(lambda x: int(x), self.vectorB.split(","))),
            list(map(lambda x: int(x), self.vectorC.split(",")))
        )
        self.vacuums = (
            int(self.vacuumA),
            int(self.vacuumB),
            int(self.vacuumC)
        )
        self.ribbonTolerance = float(self.ribbonTolerance)
        self.fixedRibbonWidth = float(self.fixedRibbonWidth)
        self.savedPath = Path(self.savedPath)
        self.saveFilePath = self.savedPath / self.choiceStructure
        self.minRibbonWidth = float(self.minRibbonWidth)
        self.maxRibbonWidth = float(self.maxRibbonWidth)
        self.ifWidthTest = int(self.ifWidthTest)
        self.ifShowTargetStructure = int(self.ifShowTargetStructure)
        self.terminateAtom = self.terminateAtom
        self.data = {}  # 用于储存原始结构数据
        self.loadYamlCif()

    def show_ribbon(self, ribbon):
        ase_gui = ASEGUI(None, ribbon, self.repeatImages)
        ase_gui.show()

    def run(self) -> None:
        for ribbon in self.buildRibbon():
            ribbon_width = self.getRibbonWidth(ribbon)
            print(f"当前纳米带宽度为：{ribbon_width}....")
            if self.fixedRibbonWidth:  # 满足固定宽度ribbon时
                if self.terminateAtom:
                    _ribbon = RibbonBuilder.terminate(ribbon, symbol=self.terminateAtom, side=2,
                                                      connectivity_opts=self.connectivity)
                else:
                    _ribbon = RibbonBuilder.edge_del(ribbon, self.ribbonTolerance)
                fixedWidth = self.fixedRibbonWidth
                ribbon_width = float(f"{ribbon_width:.2f}")
                if ribbon_width > fixedWidth:
                    break
                if fixedWidth <= ribbon_width < fixedWidth + 0.01:
                    if self.savedPath.exists():
                        _ribbon = self.reloadStructure(_ribbon)
                        print(f"达到设置的固定宽度{fixedWidth}!!\n正在保存...")
                        self.show_ribbon(_ribbon)
                        print(f"保存{self.saveStructureToYacif(_ribbon)} 成功!!!")
                    break
                print(f"未达到设置的固定宽度{fixedWidth}...")
                continue
            if self.minRibbonWidth < ribbon_width < self.maxRibbonWidth:  # 满足指定宽度ribbon时
                if self.terminateAtom:
                    _ribbon = RibbonBuilder.terminate(ribbon, symbol=self.terminateAtom, side=2,
                                                      connectivity_opts=self.connectivity)
                else:
                    _ribbon = RibbonBuilder.edge_del(ribbon, self.ribbonTolerance)
                print(f"当前纳米带符合条件：{ribbon_width},正在保存...", end="    ")
                if self.ifShowTargetStructure:
                    self.show_ribbon(_ribbon)
                print(f"保存{self.saveStructureToYacif(_ribbon)} 成功!!!")
                break
            if self.ifWidthTest:  # 当条件不满足时，是否展示结构
                self.show_ribbon(RibbonBuilder.edge_del(ribbon, self.ribbonTolerance))

    def saveStructureToYacif(self, ribbon):
        # 将后缀名统一为".cif",并写入cif文件
        if self.saveFilePath.suffix == ".yacif":
            saveFilePath = self.saveFilePath.__str__().rsplit(".", maxsplit=1)[0] + ".cif"
        else:
            saveFilePath = self.saveFilePath
        ribbon.write(saveFilePath, "cif")
        # 读取cif文件内容
        saveFilePath = Path(saveFilePath)
        cif = saveFilePath.read_text(encoding="utf-8")

        yacifName = f"{self.choiceStructure.rsplit('.', maxsplit=1)[0]}_{md5_hex(saveFilePath)}.yacif"
        yacifPath = self.savedPath / yacifName
        with yacifPath.open(mode="w+", encoding="utf-8") as fd:
            yaml.dump({"guiInfo": self.guiConfig, "cif": cif, "structureInfo": self.data["structureInfo"]}, fd)
        Path(saveFilePath).unlink(missing_ok=True)
        return yacifPath.__str__()

    @staticmethod
    def reloadStructure(atoms):
        with BytesIO() as b1:  # reload structure from cif
            atoms.write(b1, "cif")
            b1.seek(0)
            cif_block = parse_cif_ase(b1)
            return list(cif_block)[0].get_atoms()

    def buildRibbon(self):
        atoms = parse_cif_ase_string(self.data["cif"])
        for i in range(self.bottom, self.top):
            layer = 2 + self.widthControlBase + self.widthControlDelta * i
            ribbon = RibbonBuilder.build(atoms, layer, self.widthControlOrigo, self.ribbonTolerance,
                                         milerIndex=self.milerIndex, vacuums=self.vacuums)
            yield ribbon

    @staticmethod
    def getRibbonWidth(ribbon):
        _ribbon = ribbon.copy()
        _ribbon = RibbonBuilder.edge_del(_ribbon)
        width = RibbonBuilder.get_ribbon_width(_ribbon)
        return width

    def loadYamlCif(self):
        if self.filePath.suffix == ".yacif":

            with open(self.filePath, encoding="utf-8") as fd:
                data = yaml.load(fd, Loader=yaml.FullLoader)
                self.data.update(data)
        else:
            self.data["cif"] = self.filePath.read_text(encoding="utf-8")
            self.data["structureInfo"] = {}
