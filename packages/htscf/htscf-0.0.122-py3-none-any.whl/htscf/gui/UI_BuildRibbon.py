# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_BuildRibbon.ui'
##
## Created by: Qt User Interface Compiler version 6.2.4
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QAction, QBrush, QColor, QConicalGradient,
                           QCursor, QFont, QFontDatabase, QGradient,
                           QIcon, QImage, QKeySequence, QLinearGradient,
                           QPainter, QPalette, QPixmap, QRadialGradient,
                           QTransform)
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
                               QGridLayout, QGroupBox, QLabel, QLineEdit,
                               QMainWindow, QMenu, QMenuBar, QPushButton,
                               QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
                               QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"Ribbon Builder")
        MainWindow.resize(640, 680)
        MainWindow.setMaximumSize(QSize(640, 680))
        # MainWindow.setStyleSheet(u"\n"
        #                          "QPushButton{\n"
        #                          "    background-color: #4CAF50; /* Green */\n"
        #                          "    border: none;\n"
        #                          "    color: white;\n"
        #                          "\n"
        #                          "\n"
        #                          "	border-radius:4px\n"
        #                          "}\n"
        #                          "QPushButton:hover{\n"
        #                          "	background:rgb(0, 255, 127);\n"
        #                          "	color:black;\n"
        #                          "	cursor:pointer\n"
        #                          "}\n"
        #                          "QLineEdit{\n"
        #                          "	width:40px\n"
        #                          "}\n"
        #                          "")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.rootPath = QLineEdit(self.centralWidget)
        self.rootPath.setObjectName(u"rootPath")
        self.rootPath.setReadOnly(True)

        self.gridLayout.addWidget(self.rootPath, 0, 1, 1, 1)

        self.label_3 = QLabel(self.centralWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.centralWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.choiceStructure = QComboBox(self.centralWidget)
        self.choiceStructure.setObjectName(u"choiceStructure")

        self.gridLayout.addWidget(self.choiceStructure, 1, 1, 1, 1)

        self.saveToPath = QPushButton(self.centralWidget)
        self.saveToPath.setObjectName(u"saveToPath")

        self.gridLayout.addWidget(self.saveToPath, 2, 3, 1, 1)

        self.backRootPath = QPushButton(self.centralWidget)
        self.backRootPath.setObjectName(u"backRootPath")

        self.gridLayout.addWidget(self.backRootPath, 0, 3, 1, 1)

        self.nextStructure = QPushButton(self.centralWidget)
        self.nextStructure.setObjectName(u"nextStructure")

        self.gridLayout.addWidget(self.nextStructure, 1, 2, 1, 2)

        self.savedPath = QLineEdit(self.centralWidget)
        self.savedPath.setObjectName(u"savedPath")

        self.gridLayout.addWidget(self.savedPath, 2, 1, 1, 1)

        self.openSavePath = QPushButton(self.centralWidget)
        self.openSavePath.setObjectName(u"openSavePath")

        self.gridLayout.addWidget(self.openSavePath, 2, 2, 1, 1)

        self.label_2 = QLabel(self.centralWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.openRootPath = QPushButton(self.centralWidget)
        self.openRootPath.setObjectName(u"openRootPath")

        self.gridLayout.addWidget(self.openRootPath, 0, 2, 1, 1)

        self.verticalLayout_2.addLayout(self.gridLayout)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.groupBox_2 = QGroupBox(self.centralWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.vectorA = QComboBox(self.groupBox_2)
        self.vectorA.setObjectName(u"vectorA")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.vectorA)

        self.label_17 = QLabel(self.groupBox_2)
        self.label_17.setObjectName(u"label_17")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_17)

        self.vectorB = QComboBox(self.groupBox_2)
        self.vectorB.setObjectName(u"vectorB")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.vectorB)

        self.label_18 = QLabel(self.groupBox_2)
        self.label_18.setObjectName(u"label_18")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_18)

        self.vectorC = QComboBox(self.groupBox_2)
        self.vectorC.setObjectName(u"vectorC")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.vectorC)

        self.gridLayout_3.addLayout(self.formLayout, 0, 0, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.toggleVectorAB = QPushButton(self.groupBox_2)
        self.toggleVectorAB.setObjectName(u"toggleVectorAB")
        self.toggleVectorAB.setMaximumSize(QSize(130, 16777215))

        self.gridLayout_2.addWidget(self.toggleVectorAB, 0, 0, 1, 2)

        self.setVectorZigzag = QPushButton(self.groupBox_2)
        self.setVectorZigzag.setObjectName(u"setVectorZigzag")
        self.setVectorZigzag.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.setVectorZigzag, 1, 0, 1, 1)

        self.setVectorArmchair = QPushButton(self.groupBox_2)
        self.setVectorArmchair.setObjectName(u"setVectorArmchair")
        self.setVectorArmchair.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.setVectorArmchair, 1, 1, 1, 1)

        self.setVectorHorizontal = QPushButton(self.groupBox_2)
        self.setVectorHorizontal.setObjectName(u"setVectorHorizontal")
        self.setVectorHorizontal.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.setVectorHorizontal, 2, 0, 1, 1)

        self.setVectorVertical = QPushButton(self.groupBox_2)
        self.setVectorVertical.setObjectName(u"setVectorVertical")
        self.setVectorVertical.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.setVectorVertical, 2, 1, 1, 1)

        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_4, 1, 1, 1, 1)

        self.gridLayout_8.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.groupBox = QGroupBox(self.centralWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.widthControlDelta = QComboBox(self.groupBox)
        self.widthControlDelta.setObjectName(u"widthControlDelta")

        self.gridLayout_7.addWidget(self.widthControlDelta, 1, 1, 1, 1)

        self.widthControlOrigo = QComboBox(self.groupBox)
        self.widthControlOrigo.setObjectName(u"widthControlOrigo")

        self.gridLayout_7.addWidget(self.widthControlOrigo, 2, 1, 1, 1)

        self.setVector1_2 = QPushButton(self.groupBox)
        self.setVector1_2.setObjectName(u"setVector1_2")

        self.gridLayout_7.addWidget(self.setVector1_2, 0, 2, 1, 1)

        self.label_13 = QLabel(self.groupBox)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_7.addWidget(self.label_13, 0, 0, 1, 1)

        self.setVector2_3 = QPushButton(self.groupBox)
        self.setVector2_3.setObjectName(u"setVector2_3")

        self.gridLayout_7.addWidget(self.setVector2_3, 1, 2, 1, 1)

        self.widthControlBase = QComboBox(self.groupBox)
        self.widthControlBase.setObjectName(u"widthControlBase")

        self.gridLayout_7.addWidget(self.widthControlBase, 0, 1, 1, 1)

        self.ribbonTolerance = QLineEdit(self.groupBox)
        self.ribbonTolerance.setObjectName(u"ribbonTolerance")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ribbonTolerance.sizePolicy().hasHeightForWidth())
        self.ribbonTolerance.setSizePolicy(sizePolicy1)

        self.gridLayout_7.addWidget(self.ribbonTolerance, 3, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_7.addWidget(self.label_14, 1, 0, 1, 1)

        self.setVector2_2 = QPushButton(self.groupBox)
        self.setVector2_2.setObjectName(u"setVector2_2")

        self.gridLayout_7.addWidget(self.setVector2_2, 0, 3, 1, 1)

        self.label_16 = QLabel(self.groupBox)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_7.addWidget(self.label_16, 3, 0, 1, 1)

        self.label_15 = QLabel(self.groupBox)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_7.addWidget(self.label_15, 2, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_5, 3, 2, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_6, 3, 3, 1, 1)

        self.verticalLayout_7.addLayout(self.gridLayout_7)

        self.verticalLayout.addLayout(self.verticalLayout_7)

        self.gridLayout_8.addWidget(self.groupBox, 0, 1, 1, 1)

        self.groupBox_7 = QGroupBox(self.centralWidget)
        self.groupBox_7.setObjectName(u"groupBox_7")
        sizePolicy.setHeightForWidth(self.groupBox_7.sizePolicy().hasHeightForWidth())
        self.groupBox_7.setSizePolicy(sizePolicy)
        self.groupBox_7.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout_4 = QFormLayout(self.groupBox_7)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_12 = QLabel(self.groupBox_7)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_12)

        self.repeatA = QLineEdit(self.groupBox_7)
        self.repeatA.setObjectName(u"repeatA")

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.repeatA)

        self.label_19 = QLabel(self.groupBox_7)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_19)

        self.repeatB = QLineEdit(self.groupBox_7)
        self.repeatB.setObjectName(u"repeatB")

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.repeatB)

        self.label_20 = QLabel(self.groupBox_7)
        self.label_20.setObjectName(u"label_20")

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_20)

        self.repeatC = QLineEdit(self.groupBox_7)
        self.repeatC.setObjectName(u"repeatC")

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.repeatC)

        self.gridLayout_8.addWidget(self.groupBox_7, 1, 0, 1, 1)

        self.groupBox_5 = QGroupBox(self.centralWidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.groupBox_5)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_52 = QLabel(self.groupBox_5)
        self.label_52.setObjectName(u"label_52")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_52)

        self.minRibbonWidth = QLineEdit(self.groupBox_5)
        self.minRibbonWidth.setObjectName(u"minRibbonWidth")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.minRibbonWidth)

        self.label_50 = QLabel(self.groupBox_5)
        self.label_50.setObjectName(u"label_50")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_50)

        self.maxRibbonWidth = QLineEdit(self.groupBox_5)
        self.maxRibbonWidth.setObjectName(u"maxRibbonWidth")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.maxRibbonWidth)

        self.label_49 = QLabel(self.groupBox_5)
        self.label_49.setObjectName(u"label_49")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_49)

        self.fixedRibbonWidth = QLineEdit(self.groupBox_5)
        self.fixedRibbonWidth.setObjectName(u"fixedRibbonWidth")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.fixedRibbonWidth)

        self.gridLayout_8.addWidget(self.groupBox_5, 1, 1, 1, 1)

        self.groupBox_4 = QGroupBox(self.centralWidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout_6 = QFormLayout(self.groupBox_4)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_22 = QLabel(self.groupBox_4)
        self.label_22.setObjectName(u"label_22")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.label_22)

        self.vacuumA = QLineEdit(self.groupBox_4)
        self.vacuumA.setObjectName(u"vacuumA")

        self.formLayout_6.setWidget(0, QFormLayout.FieldRole, self.vacuumA)

        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_6.setWidget(1, QFormLayout.LabelRole, self.label_10)

        self.vacuumB = QLineEdit(self.groupBox_4)
        self.vacuumB.setObjectName(u"vacuumB")

        self.formLayout_6.setWidget(1, QFormLayout.FieldRole, self.vacuumB)

        self.label_11 = QLabel(self.groupBox_4)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_6.setWidget(2, QFormLayout.LabelRole, self.label_11)

        self.vacuumC = QLineEdit(self.groupBox_4)
        self.vacuumC.setObjectName(u"vacuumC")

        self.formLayout_6.setWidget(2, QFormLayout.FieldRole, self.vacuumC)

        self.gridLayout_8.addWidget(self.groupBox_4, 2, 0, 1, 1)

        self.groupBox_6 = QGroupBox(self.centralWidget)
        self.groupBox_6.setObjectName(u"groupBox_6")
        sizePolicy.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy)
        self.formLayout_7 = QFormLayout(self.groupBox_6)
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.label_7 = QLabel(self.groupBox_6)
        self.label_7.setObjectName(u"label_7")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy2)
        self.label_7.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.formLayout_7.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.formLayout_5.setFormAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.label_9 = QLabel(self.groupBox_6)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_9)

        self.connectivityMin = QLineEdit(self.groupBox_6)
        self.connectivityMin.setObjectName(u"connectivityMin")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.connectivityMin.sizePolicy().hasHeightForWidth())
        self.connectivityMin.setSizePolicy(sizePolicy3)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.connectivityMin)

        self.label_23 = QLabel(self.groupBox_6)
        self.label_23.setObjectName(u"label_23")

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.label_23)

        self.connectivityMax = QLineEdit(self.groupBox_6)
        self.connectivityMax.setObjectName(u"connectivityMax")
        sizePolicy3.setHeightForWidth(self.connectivityMax.sizePolicy().hasHeightForWidth())
        self.connectivityMax.setSizePolicy(sizePolicy3)

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.connectivityMax)

        self.formLayout_7.setLayout(0, QFormLayout.FieldRole, self.formLayout_5)

        self.label_45 = QLabel(self.groupBox_6)
        self.label_45.setObjectName(u"label_45")
        sizePolicy2.setHeightForWidth(self.label_45.sizePolicy().hasHeightForWidth())
        self.label_45.setSizePolicy(sizePolicy2)

        self.formLayout_7.setWidget(1, QFormLayout.LabelRole, self.label_45)

        self.bottom = QLineEdit(self.groupBox_6)
        self.bottom.setObjectName(u"bottom")
        sizePolicy3.setHeightForWidth(self.bottom.sizePolicy().hasHeightForWidth())
        self.bottom.setSizePolicy(sizePolicy3)

        self.formLayout_7.setWidget(1, QFormLayout.FieldRole, self.bottom)

        self.label_21 = QLabel(self.groupBox_6)
        self.label_21.setObjectName(u"label_21")
        sizePolicy2.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy2)

        self.formLayout_7.setWidget(2, QFormLayout.LabelRole, self.label_21)

        self.top = QLineEdit(self.groupBox_6)
        self.top.setObjectName(u"top")
        sizePolicy3.setHeightForWidth(self.top.sizePolicy().hasHeightForWidth())
        self.top.setSizePolicy(sizePolicy3)

        self.formLayout_7.setWidget(2, QFormLayout.FieldRole, self.top)

        self.gridLayout_8.addWidget(self.groupBox_6, 2, 1, 1, 1)

        self.groupBox_3 = QGroupBox(self.centralWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.ifWidthTest = QCheckBox(self.groupBox_3)
        self.ifWidthTest.setObjectName(u"ifWidthTest")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.ifWidthTest)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.ifShowTargetStructure = QCheckBox(self.groupBox_3)
        self.ifShowTargetStructure.setObjectName(u"ifShowTargetStructure")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.ifShowTargetStructure)

        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self.terminateAtom = QComboBox(self.groupBox_3)
        self.terminateAtom.setObjectName(u"terminateAtom")
        self.terminateAtom.setMaximumSize(QSize(80, 16777215))

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.terminateAtom)

        self.gridLayout_8.addWidget(self.groupBox_3, 3, 0, 1, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_8)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.showStructure = QPushButton(self.centralWidget)
        self.showStructure.setObjectName(u"showStructure")

        self.gridLayout_4.addWidget(self.showStructure, 0, 0, 1, 1)

        self.runProgram = QPushButton(self.centralWidget)
        self.runProgram.setObjectName(u"runProgram")

        self.gridLayout_4.addWidget(self.runProgram, 0, 1, 1, 1)

        self.stopProgram = QPushButton(self.centralWidget)
        self.stopProgram.setObjectName(u"stopProgram")

        self.gridLayout_4.addWidget(self.stopProgram, 0, 2, 1, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_4)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 26))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuWindow = QMenu(self.menubar)
        self.menuWindow.setObjectName(u"menuWindow")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menu.addAction(self.actionOpen)
        self.menu.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        self.openRootPath.clicked.connect(MainWindow.openFilesSlot)
        self.backRootPath.clicked.connect(MainWindow.openFilesSlot)
        self.openSavePath.clicked.connect(MainWindow.openFilesSlot)
        self.nextStructure.clicked.connect(MainWindow.nextStructureSlot)
        self.rootPath.textChanged.connect(MainWindow.loadStructuresSlot)
        self.choiceStructure.currentTextChanged.connect(MainWindow.parseStructureSlot)
        self.saveToPath.clicked.connect(MainWindow.saveToPathSlot)
        self.setVector1_2.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVector2_2.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVector2_3.clicked.connect(MainWindow.changeComboBoxSlot)
        self.toggleVectorAB.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVectorZigzag.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVectorArmchair.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVectorHorizontal.clicked.connect(MainWindow.changeComboBoxSlot)
        self.setVectorVertical.clicked.connect(MainWindow.changeComboBoxSlot)
        self.runProgram.clicked.connect(MainWindow.taskHandlerSlot)
        self.stopProgram.clicked.connect(MainWindow.taskHandlerSlot)
        self.showStructure.clicked.connect(MainWindow.showStructureSlot)
        self.actionOpen.triggered.connect(MainWindow.openFilesSlot)
        self.actionExit.triggered.connect(MainWindow.close)
        self.actionAbout.triggered.connect(MainWindow.getHelp)
        self.nextStructure.clicked.connect(MainWindow.changeShowStructureSlot)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ribbon Builder", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Save Path:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Root:", None))
        self.saveToPath.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.backRootPath.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.nextStructure.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.openSavePath.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Structure:", None))
        self.openRootPath.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Vector", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"a", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"b", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"c", None))
        self.toggleVectorAB.setText(QCoreApplication.translate("MainWindow", u"toggleVector A B", None))
        self.setVectorZigzag.setText(QCoreApplication.translate("MainWindow", u"Zigzag", None))
        self.setVectorArmchair.setText(QCoreApplication.translate("MainWindow", u"Armchair", None))
        self.setVectorHorizontal.setText(QCoreApplication.translate("MainWindow", u"Horizontal", None))
        self.setVectorVertical.setText(QCoreApplication.translate("MainWindow", u"Vertical", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Width Control", None))
        self.setVector1_2.setText(QCoreApplication.translate("MainWindow", u"1-2", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Base:", None))
        self.setVector2_3.setText(QCoreApplication.translate("MainWindow", u"2-3", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Delta:", None))
        self.setVector2_2.setText(QCoreApplication.translate("MainWindow", u"2-2", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Ribbon Tolerance:", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Origo:", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Repeat", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"a", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"b", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"c", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Ribbon Width", None))
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Min", None))
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"Max", None))
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"Fixed", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Vacuum", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"A-Axis:", None))
        self.vacuumA.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"B-Axis:", None))
        self.vacuumB.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"C-Axis:", None))
        self.vacuumC.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.groupBox_6.setTitle("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Connectivity", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"min:", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"max:", None))
        self.label_45.setText(QCoreApplication.translate("MainWindow", u"Bottom:", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Top:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Options", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Width Test", None))
        self.ifWidthTest.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Show Target Structure", None))
        self.ifShowTargetStructure.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Terminate Atom:", None))
        self.showStructure.setText(QCoreApplication.translate("MainWindow", u"Show", None))
        self.runProgram.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.stopProgram.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuWindow.setTitle(QCoreApplication.translate("MainWindow", u"Window", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi
