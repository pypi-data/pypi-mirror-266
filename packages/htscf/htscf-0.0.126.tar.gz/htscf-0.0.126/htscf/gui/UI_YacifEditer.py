# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_YacifEditer.ui'
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
from PySide2.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QLabel, QLineEdit, QListView, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(657, 393)
        self.actionOpenFile = QAction(MainWindow)
        self.actionOpenFile.setObjectName(u"actionOpenFile")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.filePath = QLineEdit(self.centralwidget)
        self.filePath.setObjectName(u"filePath")

        self.gridLayout_2.addWidget(self.filePath, 0, 1, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.savePath = QLineEdit(self.centralwidget)
        self.savePath.setObjectName(u"savePath")

        self.gridLayout_2.addWidget(self.savePath, 2, 1, 1, 1)

        self.nextFile = QPushButton(self.centralwidget)
        self.nextFile.setObjectName(u"nextFile")

        self.gridLayout_2.addWidget(self.nextFile, 3, 4, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.fileName = QComboBox(self.centralwidget)
        self.fileName.setObjectName(u"fileName")

        self.gridLayout_2.addWidget(self.fileName, 3, 1, 1, 1)

        self.showYacif = QPushButton(self.centralwidget)
        self.showYacif.setObjectName(u"showYacif")

        self.gridLayout_2.addWidget(self.showYacif, 3, 3, 1, 1)

        self.openSavePath = QPushButton(self.centralwidget)
        self.openSavePath.setObjectName(u"openSavePath")

        self.gridLayout_2.addWidget(self.openSavePath, 2, 3, 1, 1)

        self.openFilePath = QPushButton(self.centralwidget)
        self.openFilePath.setObjectName(u"openFilePath")

        self.gridLayout_2.addWidget(self.openFilePath, 0, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.listView = QListView(self.centralwidget)
        self.listView.setObjectName(u"listView")
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.listView)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 657, 26))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        self.menu_2 = QMenu(self.menubar)
        self.menu_2.setObjectName(u"menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menu.addAction(self.actionOpenFile)
        self.menu.addAction(self.actionExit)
        self.menu_2.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        self.actionOpenFile.triggered.connect(MainWindow.openFileSlot)
        self.openFilePath.clicked.connect(MainWindow.openFileSlot)
        self.openSavePath.clicked.connect(MainWindow.openFileSlot)
        self.filePath.textChanged.connect(MainWindow.loadYacifSlot)
        self.fileName.currentIndexChanged.connect(MainWindow.openYacifSlot)
        self.showYacif.clicked.connect(MainWindow.openYacifSlot)
        self.nextFile.clicked.connect(MainWindow.nextYacifSlot)
        self.listView.doubleClicked.connect(MainWindow.deleteRowSlot)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Yacif\u7f16\u8f91\u5668", None))
        self.actionOpenFile.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Save Path\uff1a", None))
        self.nextFile.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Path\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Yacif:", None))
        self.showYacif.setText(QCoreApplication.translate("MainWindow", u"Show", None))
        self.openSavePath.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.openFilePath.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.menu_2.setTitle(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9", None))
    # retranslateUi

