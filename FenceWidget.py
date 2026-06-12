import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor

CONFIG_FILE = "folder_data.json"


# --- СЛОЙ ДАННЫХ ---
class FolderDataManager:
    def __init__(self):
        self.saved_paths = []
        self.load_data()

    def load_data(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    paths = json.load(f)
                    self.saved_paths = [p for p in paths if os.path.exists(p)]
            except Exception as e:
                print(f"Error loading data: {e}")

    def save_data(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.saved_paths, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_path(self, path):
        if path and path not in self.saved_paths:
            self.saved_paths.append(path)
            self.save_data()
            return True
        return False

    def remove_path(self, path):
        if path in self.saved_paths:
            self.saved_paths.remove(path)
            self.save_data()
            return True
        return False


# --- КАСТОМНЫЙ ВИДЖЕТ ИКОНКИ (БЕЗ КОНФЛИКТОВ С WINDOWS) ---
class DraggableAppIcon(QLabel):
    def __init__(self, path, parent_window):
        super().__init__()
        self.path = path
        self.parent_window = parent_window
        self.drag_start_pos = QPoint()

        self.setFixedSize(50, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        file_name = os.path.basename(path)
        if len(file_name) > 8:
            file_name = file_name[:6] + ".."

        self.setText(f"📄\n{file_name}")
        self.setStyleSheet("""
            QLabel {
                color: white; 
                font-size: 9px;
                border: 1px dashed rgba(255,255,255,0.15);
                border-radius: 8px;
            }
            QLabel:hover { background-color: rgba(255,255,255,0.1); }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.MouseButton.LeftButton:
            return
        if (event.position().toPoint() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        # Архитектурное исправление: передаем пустой кастомный текст "remove_me",
        # чтобы Windows не пыталась копировать/переносить реальный файл на диске
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText("remove_me")
        drag.setMimeData(mime_data)

        # Рисуем фантом иконки при перетаскивании
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        # Запускаем перенос. Нам не важно, куда пользователь отпустит мышь за пределами окна
        drag.exec(Qt.DropAction.CopyAction)

        # Как только мышь отпустили вне нашей папки — мгновенно удаляем её из панели
        # без вызова дублирующих окон проводника Windows
        self.parent_window.remove_app(self.path)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and (
                event.position().toPoint() - self.drag_start_pos).manhattanLength() < 5:
            os.startfile(self.path)


# --- ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ ---
class AndroidFolder(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = FolderDataManager()
        self.old_pos = QPoint()
        self.is_dragging = False

        self.main_layout = QVBoxLayout()
        self.folder_button = QPushButton("📁 Мои Программы", self)
        self.apps_panel = QWidget()
        self.grid_layout = QGridLayout()

        self.initUI()
        self.redraw_grid()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(True)

        self.folder_button.setFixedSize(150, 40)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(240, 240, 240, 0.95);
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #ccc;
                color: black;
            }
            QPushButton:hover { background-color: rgba(220, 220, 220, 1); }
        """)

        self.folder_button.mousePressEvent = self.mousePressEvent
        self.folder_button.mouseMoveEvent = self.mouseMoveEvent
        self.folder_button.mouseReleaseEvent = self.mouseReleaseEvent

        self.main_layout.addWidget(self.folder_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apps_panel.setStyleSheet("""
            background-color: rgba(30, 30, 30, 0.93); 
            border-radius: 12px;
            padding: 8px;
        """)
        self.grid_layout.setSpacing(6)
        self.apps_panel.setLayout(self.grid_layout)
        self.apps_panel.setVisible(False)

        self.main_layout.addWidget(self.apps_panel)
        self.setLayout(self.main_layout)
        self.resize(160, 60)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull():
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            if delta.manhattanLength() > 5:
                self.is_dragging = True
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = QPoint()
            if not self.is_dragging:
                self.toggle_folder()
            self.is_dragging = False

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        updated = False
        for url in event.mimeData().urls():
            if self.data_manager.add_path(url.toLocalFile()):
                updated = True

        if updated:
            self.redraw_grid()
        if not self.apps_panel.isVisible():
            self.toggle_folder()

    def remove_app(self, path):
        if self.data_manager.remove_path(path):
            self.redraw_grid()

    def redraw_grid(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for index, path in enumerate(self.data_manager.saved_paths):
            row = index // 4
            col = index % 4

            icon_widget = DraggableAppIcon(path, self)
            self.grid_layout.addWidget(icon_widget, row, col)

        self.update_window_size()

    def toggle_folder(self):
        self.apps_panel.setVisible(not self.apps_panel.isVisible())
        self.update_window_size()

    def update_window_size(self):
        count = len(self.data_manager.saved_paths)
        if self.apps_panel.isVisible() and count > 0:
            cols = min(4, count)
            rows = (count + 3) // 4
            width = max(160, cols * 56 + 24)
            height = 50 + (rows * 56 + 16)
            self.resize(width, height)
        else:
            self.resize(160, 60)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AndroidFolder()
    sys.exit(app.exec())