import os
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
