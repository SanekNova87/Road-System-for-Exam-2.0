# -*- coding: utf-8 -*-
# setup_project.py
# Создаёт ВСЕ файлы проекта и запускает приложение.
# Использует картинки из resources/media

import os
import sys
import runpy
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(HERE, "resources", "media")

FILES = {}

# ============================================================
# 1. paths.py
# ============================================================
FILES["paths.py"] = r'''import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources", "media")

def find_image(keyword):
    if not os.path.isdir(RESOURCES_DIR):
        return None
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp"):
        pattern = os.path.join(RESOURCES_DIR, ext)
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath).lower()
            if keyword.lower() in filename:
                return filepath
    return None

ROAD = find_image("road")
CROSSROADS = find_image("crossroads") or find_image("cross")
CROSS_H = find_image("cross_h") or find_image("crossing")
PEDESTRIAN = find_image("pedestrian") or find_image("ped")
TL_RED = find_image("tl_red") or find_image("traffic") or find_image("light")
BLOCK = find_image("block") or find_image("sign")
START = find_image("start")
STOP = find_image("stop") or find_image("finish")
ICON = find_image("icon")

CAR_COLORS = ("red", "blue", "green", "yellow", "orange", "purple")

def car_image(color="red"):
    if color not in CAR_COLORS:
        color = "red"
    img = find_image("car_" + color)
    if img is None:
        img = find_image("car")
    return img

CAR_BOTTOM = car_image("red")

IMAGE_FILES = {
    "road": ROAD,
    "crossroads": CROSSROADS,
    "crossing": CROSS_H,
    "pedestrian": PEDESTRIAN,
    "traffic_light": TL_RED,
    "sign": BLOCK,
    "start": START,
    "stop": STOP,
    "car": CAR_BOTTOM,
}
'''

# ============================================================
# 2. database.py
# ============================================================
FILES["database.py"] = r'''import os
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")

def init_db():
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, event_type TEXT NOT NULL, message TEXT)")
        con.commit()
        con.close()
    except Exception as e:
        print("DB init error:", e)

def log_event(event_type, message=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("INSERT INTO events (ts, event_type, message) VALUES (?, ?, ?)",
                    (ts, event_type, str(message)))
        con.commit()
        con.close()
    except Exception as e:
        print("DB log error:", e)
    print("[" + ts + "] " + str(event_type) + ": " + str(message))

def get_events(limit=200):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT ts, event_type, message FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        con.close()
        return rows
    except Exception:
        return []
'''

# ============================================================
# 3. model.py
# ============================================================
FILES["model.py"] = r'''import paths

class RoadObject:
    def __init__(self, kind, x, y, name, **props):
        self.kind = kind
        self.x = x
        self.y = y
        self.name = name
        self.rotation = 0
        self.props = dict(props) if props else {}

    def layer(self):
        return 2 if self.kind in ("car", "pedestrian") else 1

    def image_path(self):
        if self.kind == "car":
            return paths.car_image(self.props.get("color", "red"))
        return paths.IMAGE_FILES.get(self.kind, paths.BLOCK)

class RoadNetwork:
    def __init__(self):
        self.objects = {}
        self.grid = {}
        self._counter = 1

    def add(self, kind, x, y, **props):
        name = kind + "_" + str(self._counter)
        self._counter += 1
        if (x, y) in self.grid:
            old = self.grid[(x, y)]
            if old in self.objects:
                del self.objects[old]
        obj = RoadObject(kind, x, y, name, **props)
        self.objects[name] = obj
        self.grid[(x, y)] = name
        return obj

    def get(self, x, y):
        name = self.grid.get((x, y))
        return self.objects.get(name) if name else None

    def get_by_name(self, name):
        return self.objects.get(name)

    def remove(self, name):
        if name in self.objects:
            obj = self.objects[name]
            if self.grid.get((obj.x, obj.y)) == name:
                del self.grid[(obj.x, obj.y)]
            del self.objects[name]

    def sorted_by_layer(self):
        return sorted(self.objects.values(), key=lambda o: o.layer())
'''

# ============================================================
# 4. ui_mainwindow.py (БЕЗ QPainter — он в main.py)
# ============================================================
FILES["ui_mainwindow.py"] = r'''# -*- coding: utf-8 -*-
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
'''

# ============================================================
# 5. main.py — УВЕЛИЧЕННАЯ СЕТКА + ЦЕНТРИРОВАНИЕ
# ============================================================
FILES["main.py"] = r'''import os
import sys

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QPen, QColor, QTransform, QIcon, QPainter
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene,
                               QGraphicsPixmapItem, QMessageBox, QListWidgetItem,
                               QDialog, QVBoxLayout, QTextEdit, QLabel,
                               QPushButton)

from ui_mainwindow import Ui_MainWindow
from model import RoadNetwork
from database import init_db, log_event, get_events
import paths

# УВЕЛИЧЕННАЯ СЕТКА
CELL = 80
COLS = 20
ROWS = 12

PALETTE = [
    ("Дорога", "road", paths.ROAD),
    ("Перекрёсток", "crossroads", paths.CROSSROADS),
    ("Переход", "crossing", paths.CROSS_H),
    ("Пешеход", "pedestrian", paths.PEDESTRIAN),
    ("Светофор", "traffic_light", paths.TL_RED),
    ("Знак", "sign", paths.BLOCK),
    ("Старт", "start", paths.START),
    ("Финиш", "stop", paths.STOP),
    ("Машина", "car", paths.CAR_BOTTOM),
]

FALLBACK = {
    "road": (110, 110, 110),
    "crossroads": (140, 140, 140),
    "crossing": (230, 220, 120),
    "pedestrian": (60, 120, 230),
    "traffic_light": (220, 40, 40),
    "sign": (80, 80, 80),
    "start": (40, 180, 70),
    "stop": (190, 40, 40),
    "car": (220, 45, 45),
}


class LogsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Журнал событий")
        self.resize(760, 520)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Последние 200 событий (сверху - новые):"))

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        btn = QPushButton("Обновить")
        btn.clicked.connect(self.refresh)
        layout.addWidget(btn)

        self.refresh()

    def refresh(self):
        rows = get_events(200)
        if not rows:
            self.text.setText("(пусто)")
            return
        lines = ["[" + str(ts) + "] " + str(etype) + " - " + str(msg)
                 for ts, etype, msg in rows]
        self.text.setPlainText("\n".join(lines))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.network = RoadNetwork()
        self.current_kind = None
        self.selected_name = None
        self.epoch = 0

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, COLS * CELL, ROWS * CELL)
        self.graphicsView.setScene(self.scene)

        # Центрирование и сглаживание
        self.graphicsView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.graphicsView.viewport().installEventFilter(self)

        self.draw_grid()
        self.fill_palette()
        self.connect_buttons()

        if paths.ICON and os.path.exists(paths.ICON):
            self.setWindowIcon(QIcon(paths.ICON))

        init_db()
        log_event("system", "Программа запущена")
        self.statusbar.showMessage("Выберите объект слева и кликните на карте")

    def eventFilter(self, obj, event):
        if obj is self.graphicsView.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.handle_click(event)
                return True
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.handle_double_click(event)
                return True
        return super().eventFilter(obj, event)

    def cell_from_event(self, event):
        if hasattr(event, "position"):
            point = event.position().toPoint()
        else:
            point = event.pos()
        p = self.graphicsView.mapToScene(point)
        x = int(p.x() // CELL)
        y = int(p.y() // CELL)
        if 0 <= x < COLS and 0 <= y < ROWS:
            return x, y
        return None

    def handle_click(self, event):
        cell = self.cell_from_event(event)
        if cell is None:
            return
        x, y = cell

        existing = self.network.get(x, y)
        if existing is not None:
            self.select_object(existing)
            log_event("select", existing.name)
            return

        if self.current_kind is None:
            self.statusbar.showMessage("Сначала выберите объект в палитре слева")
            return

        props = {"color": "red"} if self.current_kind == "car" else {}
        obj = self.network.add(self.current_kind, x, y, **props)
        log_event("add", obj.name + " в (" + str(x) + ", " + str(y) + ")")
        self.select_object(obj)
        self.redraw()

    def handle_double_click(self, event):
        cell = self.cell_from_event(event)
        if cell is None:
            return
        obj = self.network.get(cell[0], cell[1])
        if obj is None:
            return
        obj.rotation = (obj.rotation + 90) % 360
        log_event("rotate", obj.name + " -> " + str(obj.rotation))
        self.select_object(obj)
        self.redraw()

    def fill_palette(self):
        self.listPalette.clear()
        for title, kind, icon_path in PALETTE:
            item = QListWidgetItem(title)
            pix = QPixmap(icon_path) if icon_path else QPixmap()
            if not pix.isNull():
                scaled = pix.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                item.setIcon(QIcon(scaled))
            item.setData(Qt.ItemDataRole.UserRole, kind)
            self.listPalette.addItem(item)
        self.listPalette.itemClicked.connect(self.pick_from_palette)

    def pick_from_palette(self, item):
        self.current_kind = item.data(Qt.ItemDataRole.UserRole)
        log_event("palette", "Выбран объект: " + item.text())
        self.statusbar.showMessage("Выбрано: " + item.text() + " - кликните на свободную клетку карты")

    def connect_buttons(self):
        self.btnTrain.clicked.connect(self.train)
        self.btnLoss.clicked.connect(self.show_loss)
        self.btnLogs.clicked.connect(self.show_logs)
        self.btnApply.clicked.connect(self.apply_props)
        self.btnDelete.clicked.connect(self.delete_object)
        self.comboColor.currentTextChanged.connect(self.change_color)

    def select_object(self, obj):
        self.selected_name = obj.name
        self.comboColor.blockSignals(True)
        self.spinRotate.blockSignals(True)
        self.editName.setText(obj.name)
        self.comboColor.setCurrentText(obj.props.get("color", "red"))
        self.spinRotate.setValue(obj.rotation)
        self.spinRotate.blockSignals(False)
        self.comboColor.blockSignals(False)
        self.statusbar.showMessage("Выбран: " + obj.name + " | двойной клик = поворот на 90 градусов")

    def draw_grid(self):
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(2)
        for x in range(0, COLS * CELL + 1, CELL):
            self.scene.addLine(x, 0, x, ROWS * CELL, pen)
        for y in range(0, ROWS * CELL + 1, CELL):
            self.scene.addLine(0, y, COLS * CELL, y, pen)

    def redraw(self):
        self.scene.clear()
        self.draw_grid()

        for obj in self.network.sorted_by_layer():
            pix = QPixmap(obj.image_path()) if obj.image_path() else QPixmap()

            if pix.isNull():
                pix = QPixmap(CELL, CELL)
                rgb = FALLBACK.get(obj.kind, (150, 150, 150))
                if obj.kind == "car":
                    color_name = obj.props.get("color", "red")
                    try:
                        pix.fill(QColor(color_name))
                    except Exception:
                        pix.fill(QColor(rgb[0], rgb[1], rgb[2]))
                else:
                    pix.fill(QColor(rgb[0], rgb[1], rgb[2]))
            else:
                pix = pix.scaled(CELL, CELL, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            if obj.rotation:
                tr = QTransform()
                tr.rotate(obj.rotation)
                pix = pix.transformed(tr)

            item = QGraphicsPixmapItem(pix)
            item.setPos(obj.x * CELL, obj.y * CELL)
            item.setZValue(obj.layer())
            self.scene.addItem(item)

    def apply_props(self):
        name = self.editName.text().strip()
        obj = self.network.get_by_name(name)
        if obj is None:
            QMessageBox.warning(self, "Внимание", "Объект с именем '" + name + "' не найден.\nСначала кликните по объекту на карте.")
            return
        obj.rotation = self.spinRotate.value()
        if obj.kind == "car":
            obj.props["color"] = self.comboColor.currentText()
        log_event("apply", name + ": поворот " + str(obj.rotation) + ", цвет " + str(obj.props.get("color", "-")))
        self.redraw()

    def change_color(self, value):
        obj = self.network.get_by_name(self.selected_name or "")
        if obj is not None and obj.kind == "car":
            obj.props["color"] = value
            log_event("color", obj.name + " -> " + value)
            self.redraw()

    def delete_object(self):
        name = self.editName.text().strip()
        obj = self.network.get_by_name(name)
        if obj is None:
            QMessageBox.warning(self, "Внимание", "Сначала выберите объект на карте.")
            return
        self.network.remove(name)
        log_event("delete", name)
        self.selected_name = None
        self.editName.clear()
        self.redraw()

    def train(self):
        self.epoch += 1
        self.btnTrain.setText("Обучение (" + str(self.epoch) + " эпоха)")
        self.lblTrain.setText("Эпоха " + str(self.epoch) + " - нажмите снова")
        log_event("train", "Эпоха " + str(self.epoch))
        self.statusbar.showMessage("Обучение: эпоха " + str(self.epoch))

    def show_loss(self):
        loss = max(0.0, 1.0 - self.epoch * 0.1)
        text = "Эпох пройдено: " + str(self.epoch) + "\nПотери: " + format(loss, ".2f")
        log_event("loss", text.replace("\n", " | "))
        QMessageBox.information(self, "Процесс обучения", text)

    def show_logs(self):
        log_event("logs", "Открыт журнал событий")
        dlg = LogsDialog(self)
        dlg.exec()


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("RoadEditor")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''

# ============================================================
# 6. README.txt
# ============================================================
FILES["README.txt"] = r'''РЕДАКТОР ДОРОЖНОЙ СЕТИ
=====================

ЗАПУСК:
    python setup_project.py

ИЗМЕНЕНИЯ:
- Сетка увеличена: клетки 80x80 пикселей
- Размер карты: 20x12 клеток
- Сетка центрирована в окне
- Картинки автоматически масштабируются под размер клетки

УПРАВЛЕНИЕ:
    1. Выберите объект в левой панели "Объекты".
    2. Кликните по свободной клетке карты - объект добавится.
    3. Кликните по существующему объекту - его свойства появятся справа.
    4. Двойной клик по объекту - поворот на 90 градусов.
    5. Справа можно изменить цвет (для машины) и поворот, нажать "Применить".
    6. "Удалить" удаляет выбранный объект.
    7. "Обучение" считает эпохи, "Потери" показывает значение потерь.
    8. "Логи" открывает журнал событий.

БАЗА ДАННЫХ:
    events.db  ->  таблица events (id, ts, event_type, message)

КАРТИНКИ:
    resources\media\  - папка с изображениями.
    Скрипт автоматически ищет файлы по ключевым словам в именах файлов.
'''


# ============================================================
# Функции установщика
# ============================================================
def write_files():
    print("=" * 64)
    print("СОЗДАНИЕ ПРОЕКТА")
    print("Папка:", HERE)
    print("=" * 64)

    for name, content in FILES.items():
        path = os.path.join(HERE, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  создан:", name, "-", os.path.getsize(path), "байт")

    cache = os.path.join(HERE, "__pycache__")
    if os.path.isdir(cache):
        for pattern in ("ui_mainwindow.*", "main.*", "model.*", "paths.*", "database.*"):
            for p in glob.glob(os.path.join(cache, pattern)):
                try:
                    os.remove(p)
                except OSError:
                    pass
    print("  старый кэш очищен")


def check_pyside():
    try:
        import PySide6
        print("PySide6:", PySide6.__version__)
        return True
    except ImportError:
        print("\nНЕ УСТАНОВЛЕН PySide6. Выполните:")
        print("    pip install PySide6")
        return False


def verify_resources():
    print("\nПроверка папки resources/media:")
    if not os.path.isdir(RESOURCES_DIR):
        print("  Папка не найдена:", RESOURCES_DIR)
        return False
    files = os.listdir(RESOURCES_DIR)
    print("  Найдено файлов:", len(files))
    return True


def verify_ui():
    import ui_mainwindow
    if not hasattr(ui_mainwindow, "Ui_MainWindow"):
        raise RuntimeError("В ui_mainwindow.py нет класса Ui_MainWindow")
    print("\nПроверка импорта: OK")


def main():
    os.chdir(HERE)
    if HERE not in sys.path:
        sys.path.insert(0, HERE)

    write_files()

    if not check_pyside():
        sys.exit(1)

    verify_resources()
    verify_ui()

    print("\n" + "=" * 64)
    print("ЗАПУСК ПРИЛОЖЕНИЯ")
    print("Сетка: 20x12 клеток по 80x80 пикселей")
    print("=" * 64)

    runpy.run_path(os.path.join(HERE, "main.py"), run_name="__main__")


if __name__ == "__main__":
    main()