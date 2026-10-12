# -*- coding: utf-8 -*-
from PySide6.QtCore import QMetaObject, QSize, Qt
from PySide6.QtWidgets import (QComboBox, QFrame, QGraphicsView, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QSizePolicy, QSpacerItem,
                               QSpinBox, QStatusBar, QVBoxLayout, QWidget,
                               QFormLayout)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 800)

        self.centralwidget = QWidget(MainWindow)
        self.mainLayout = QVBoxLayout(self.centralwidget)

        # ВЕРХНЯЯ ПАНЕЛЬ
        self.topPanel = QFrame(self.centralwidget)
        self.topPanel.setFrameShape(QFrame.Shape.Box)
        self.topPanel.setMinimumSize(QSize(0, 80))
        self.topLayout = QHBoxLayout(self.topPanel)

        self.trainBox = QVBoxLayout()
        self.btnTrain = QPushButton("Обучение (1 эпоха)", self.topPanel)
        self.btnTrain.setMinimumSize(QSize(180, 40))
        self.lblTrain = QLabel("Начать обучение", self.topPanel)
        self.lblTrain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trainBox.addWidget(self.btnTrain)
        self.trainBox.addWidget(self.lblTrain)
        self.topLayout.addLayout(self.trainBox)

        self.lossBox = QVBoxLayout()
        self.btnLoss = QPushButton("Потери", self.topPanel)
        self.btnLoss.setMinimumSize(QSize(180, 40))
        self.lblLoss = QLabel("Процесс обучения", self.topPanel)
        self.lblLoss.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lossBox.addWidget(self.btnLoss)
        self.lossBox.addWidget(self.lblLoss)
        self.topLayout.addLayout(self.lossBox)

        self.logsBox = QVBoxLayout()
        self.btnLogs = QPushButton("Логи", self.topPanel)
        self.btnLogs.setMinimumSize(QSize(180, 40))
        self.lblLogs = QLabel("Журнал событий", self.topPanel)
        self.lblLogs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logsBox.addWidget(self.btnLogs)
        self.logsBox.addWidget(self.lblLogs)
        self.topLayout.addLayout(self.logsBox)

        self.topLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.mainLayout.addWidget(self.topPanel)

        # ТРИ ПАНЕЛИ
        self.panelsLayout = QHBoxLayout()

        # Палитра
        self.groupPalette = QGroupBox("Объекты", self.centralwidget)
        self.groupPalette.setMinimumSize(QSize(180, 0))
        self.groupPalette.setMaximumSize(QSize(220, 16777215))
        self.paletteLayout = QVBoxLayout(self.groupPalette)
        self.listPalette = QListWidget(self.groupPalette)
        self.paletteLayout.addWidget(self.listPalette)
        self.panelsLayout.addWidget(self.groupPalette)

        # Карта
        self.groupMap = QGroupBox("КАРТА", self.centralwidget)
        self.mapLayout = QVBoxLayout(self.groupMap)
        self.graphicsView = QGraphicsView(self.groupMap)
        self.mapLayout.addWidget(self.graphicsView)
        self.panelsLayout.addWidget(self.groupMap)

        # Свойства
        self.groupProps = QGroupBox("Свойства", self.centralwidget)
        self.groupProps.setMinimumSize(QSize(240, 0))
        self.groupProps.setMaximumSize(QSize(300, 16777215))
        self.propsLayout = QVBoxLayout(self.groupProps)

        self.formProps = QFormLayout()

        self.lblName = QLabel("Имя:", self.groupProps)
        self.editName = QLineEdit(self.groupProps)
        self.formProps.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblName)
        self.formProps.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editName)

        self.lblColor = QLabel("Цвет:", self.groupProps)
        self.comboColor = QComboBox(self.groupProps)
        self.comboColor.addItems(["red", "blue", "green", "yellow", "orange", "purple"])
        self.formProps.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblColor)
        self.formProps.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboColor)

        self.lblRotate = QLabel("Поворот:", self.groupProps)
        self.spinRotate = QSpinBox(self.groupProps)
        self.spinRotate.setMaximum(270)
        self.spinRotate.setSingleStep(90)
        self.formProps.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblRotate)
        self.formProps.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinRotate)

        self.propsLayout.addLayout(self.formProps)

        self.btnApply = QPushButton("Применить", self.groupProps)
        self.btnApply.setMinimumSize(QSize(0, 35))
        self.propsLayout.addWidget(self.btnApply)

        self.btnDelete = QPushButton("Удалить", self.groupProps)
        self.btnDelete.setMinimumSize(QSize(0, 35))
        self.propsLayout.addWidget(self.btnDelete)

        self.propsLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.panelsLayout.addWidget(self.groupProps)

        self.mainLayout.addLayout(self.panelsLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Редактор дорожной сети")
        self.groupPalette.setTitle("Объекты")
        self.groupMap.setTitle("КАРТА")
        self.groupProps.setTitle("Свойства")
        self.lblName.setText("Имя:")
        self.lblColor.setText("Цвет:")
        self.lblRotate.setText("Поворот:")
        self.btnApply.setText("Применить")
        self.btnDelete.setText("Удалить")
