import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QMenu, QMessageBox, QLineEdit, QSizePolicy, QGridLayout, QDialog,
    QFormLayout, QFileDialog, QSpacerItem, QLabel, QStyle
)
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QSize, QPoint, pyqtSignal, QEasingCurve, QUrl
from PyQt5.Qt import QDesktopServices
import qtawesome as qta


class AppIcon(QPushButton):
    remove_requested = pyqtSignal(dict)
    edit_requested = pyqtSignal(dict)
    open_requested = pyqtSignal(dict)

    def __init__(self, app_info, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.setFlat(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(app_info["name"])

        default_icon_path = "../../../Desktop/PyCharm/EasyGameLauncher/default_icon.png"

        # Set icon, or use a default icon with proper size
        icon_path = app_info.get("icon")
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            if os.path.exists(default_icon_path):
                self.setIcon(QIcon(default_icon_path))
            else:
                default_icon = self.style().standardIcon(QStyle.SP_FileIcon).pixmap(64, 64)
                resized_default_icon = default_icon.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setIcon(QIcon(resized_default_icon))

        self.setIconSize(QSize(64, 64))  # Same size for all icons
        self.setFixedSize(100, 100)
        self.setStyleSheet("background-color: transparent; border: none;")
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.parent().parent().launch_application(self.app_info)
        self.animate_bounce()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        main_window = self.parent().parent()
        menu.setStyleSheet(main_window.get_menu_style())
        menu.addAction("Open").triggered.connect(lambda: self.open_requested.emit(self.app_info))
        menu.addAction("Edit").triggered.connect(lambda: self.edit_requested.emit(self.app_info))
        menu.addAction("Remove").triggered.connect(lambda: self.remove_requested.emit(self.app_info))
        menu.exec_(self.mapToGlobal(event.pos()))

    def animate_bounce(self):
        animation = QPropertyAnimation(self, b"geometry")
        original = self.geometry()
        animation.setDuration(500)
        animation.setKeyValueAt(0, original)
        animation.setKeyValueAt(0.25, QRect(original.x(), original.y() - 20, original.width(), original.height()))
        animation.setKeyValueAt(0.5, original)
        animation.setKeyValueAt(0.75, QRect(original.x(), original.y() - 10, original.width(), original.height()))
        animation.setKeyValueAt(1, original)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.start()
        self.animation = animation


class AddEditIconDialog(QDialog):
    def __init__(self, title, current_theme, prefill_data=None, parent=None):
        super().__init__(parent)
        self.current_theme = current_theme
        self.setWindowTitle(title)
        self.setFixedSize(400, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove the "?" button
        self.setModal(True)
        self.setup_ui(prefill_data)

    def setup_ui(self, prefill_data):
        layout = QFormLayout(self)
        self.name_input = QLineEdit(prefill_data.get("name", "") if prefill_data else "", self)
        self.command_input = QLineEdit(prefill_data.get("command", "") if prefill_data else "", self)
        self.icon_path_input = QLineEdit(prefill_data.get("icon", "") if prefill_data else "", self)

        icon_button = QPushButton("Select Icon", self)
        icon_button.clicked.connect(self.browse_icon)

        # Custom OK and Cancel buttons
        ok_button = QPushButton("OK", self)
        cancel_button = QPushButton("Cancel", self)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_path_input)
        icon_layout.addWidget(icon_button)

        buttons_layout = QHBoxLayout()
        buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        layout.addRow("Application Name:", self.name_input)
        layout.addRow("Command:", self.command_input)
        layout.addRow("Icon Path:", icon_layout)
        layout.addRow("", buttons_layout)

        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "dark":
            self.setStyleSheet("""
                QDialog {
                    background-color: #2e2e2e;
                    color: #d3d3d3;
                    border-radius: 10px;
                }
                QLabel {
                    color: #d3d3d3;
                }
                QLineEdit {
                    background-color: #3e3e3e;
                    color: #d3d3d3;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #555555;
                    color: #d3d3d3;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                    color: #333333;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333333;
                }
                QLineEdit {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333333;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)

    def browse_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Image Files (*.png *.jpg *.bmp *.ico)")
        if icon_path:
            self.icon_path_input.setText(icon_path)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "command": self.command_input.text(),
            "icon": self.icon_path_input.text()
        }


class AppLauncher(QMainWindow):
    SETTINGS_FILE = "../../../Desktop/PyCharm/EasyGameLauncher/settings.json"

    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.all_apps = []
        self.window_width = 700
        self.window_title = "Application Launcher"
        self.load_settings()
        self.setup_ui()
        self.setup_window()
        self.apply_theme()
        self.center_window()
        self._is_dragging = False
        self._drag_position = QPoint()
        self._is_resizing = False
        self._resize_margin = 10
        self._resize_start_pos = QPoint()
        self._initial_width = self.window_width
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    def setup_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(500)
        self.setMaximumWidth(1000)
        self.resize(self.window_width, self.height())

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.title_label = QLabel(self.window_title)
        font = self.title_label.font()
        font.setPointSize(12)
        self.title_label.setFont(font)
        self.title_label.setToolTip("Right-click to edit title")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setFixedHeight(30)
        self.title_label.mousePressEvent = self.title_mouse_press_event
        header_layout.addWidget(self.title_label)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        header_layout.addItem(spacer)

        button_size = QSize(24, 24)
        self.theme_button = QPushButton()
        self.theme_button.setIcon(qta.icon('fa.lightbulb-o', color='white'))
        self.theme_button.setIconSize(button_size)
        self.theme_button.setFixedSize(24, 24)
        self.theme_button.setStyleSheet("background-color: transparent; border: none;")
        self.theme_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)

        self.add_icon_button = QPushButton()
        self.add_icon_button.setIcon(qta.icon('fa.plus', color='white'))
        self.add_icon_button.setIconSize(button_size)
        self.add_icon_button.setFixedSize(24, 24)
        self.add_icon_button.setStyleSheet("background-color: transparent; border: none;")
        self.add_icon_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_icon_button.clicked.connect(self.open_add_icon_dialog)
        header_layout.addWidget(self.add_icon_button)

        self.close_button = QPushButton()
        self.close_button.setIcon(qta.icon('fa.close', color='white'))
        self.close_button.setIconSize(button_size)
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("background-color: transparent; border: none;")
        self.close_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_button.clicked.connect(self.close)
        header_layout.addWidget(self.close_button)

        main_layout.addLayout(header_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 18px;
                background-color: rgba(255, 255, 255, 220);
                border-radius: 10px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_icons)
        main_layout.addWidget(self.search_bar)

        self.no_icons_label = QLabel("Drag files here or use the + button to add new icons.")
        self.no_icons_label.setAlignment(Qt.AlignCenter)
        self.no_icons_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            background-color: transparent;
        """)
        self.no_icons_label.hide()
        main_layout.addWidget(self.no_icons_label)

        self.icon_layout = QGridLayout()
        self.icon_layout.setAlignment(Qt.AlignTop)
        self.icon_layout.setSpacing(20)
        main_layout.addLayout(self.icon_layout)

        self.display_icons(self.all_apps)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setMouseTracking(True)
        self.setCentralWidget(central_widget)

        self.adjust_window_height()

    def display_icons(self, apps, filtering=False):
        """
        Mostra le icone delle applicazioni basate sulla lista fornita.

        :param apps: Lista delle applicazioni da visualizzare.
        :param filtering: Se True, indica che stiamo filtrando le icone, quindi la barra di ricerca deve sempre essere visibile.
        """
        # Rimuove le icone esistenti
        for i in reversed(range(self.icon_layout.count())):
            widget = self.icon_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not apps:
            # Se non ci sono icone
            self.no_icons_label.show()
            self.search_bar.hide() if not filtering else self.search_bar.show()
        else:
            # Mostra la barra di ricerca se stiamo filtrando o se ci sono almeno 2 icone iniziali
            if filtering or len(apps) >= 2:
                self.search_bar.show()
            else:
                self.search_bar.hide()

            self.no_icons_label.hide()

            # Aggiunge le nuove icone in una griglia
            num_columns = 6
            for index, app in enumerate(apps):
                row, col = divmod(index, num_columns)
                icon = AppIcon(app, self)
                icon.remove_requested.connect(self.remove_application)
                icon.edit_requested.connect(self.edit_application)
                icon.open_requested.connect(self.launch_application)
                self.icon_layout.addWidget(icon, row, col)

        self.adjust_window_height()

    def launch_application(self, app_info):
        command = app_info.get("command")
        if command:
            if os.path.exists(command):
                QDesktopServices.openUrl(QUrl.fromLocalFile(command))
            else:
                QDesktopServices.openUrl(QUrl(command))
        else:
            QMessageBox.critical(self, "Error", "No command specified.")

    def filter_icons(self):
        search_text = self.search_bar.text().lower()
        filtered = [app for app in self.all_apps if search_text in app["name"].lower()]
        self.display_icons(filtered, filtering=True)  # Durante il filtraggio, la barra di ricerca rimane visibile

    def apply_theme(self):
        bg = "rgba(50, 50, 50, 200)" if self.current_theme == "dark" else "rgba(245, 245, 245, 220)"
        self.setStyleSheet(f"background-color: {bg}; border-radius: 15px;")
        icon_color = "#d3d3d3" if self.current_theme == "dark" else "#333333"
        self.theme_button.setIcon(qta.icon('fa.lightbulb-o', color=icon_color))
        self.close_button.setIcon(qta.icon('fa.close', color=icon_color))
        self.add_icon_button.setIcon(qta.icon('fa.plus', color=icon_color))
        search_bg = "rgba(60, 60, 60, 220)" if self.current_theme == "dark" else "rgba(255, 255, 255, 220)"
        search_text = "#d3d3d3" if self.current_theme == "dark" else "#333333"
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                font-size: 18px;
                background-color: {search_bg};
                color: {search_text};
                border-radius: 10px;
            }}
        """)
        title_color = "#d3d3d3" if self.current_theme == "dark" else "#333333"
        self.title_label.setStyleSheet(f"color: {title_color}; background-color: transparent;")
        for label in self.findChildren(QLabel):
            if label != self.title_label and label != self.no_icons_label:
                label.setStyleSheet(f"color: {'#d3d3d3' if self.current_theme == 'dark' else '#333333'};")
        self.icon_layout.setSpacing(20)

    def get_menu_style(self):
        return """
            QMenu {
                background-color: #2e2e2e;
                color: #d3d3d3;
                border: 1px solid #555555;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin-left: 5px;
                margin-right: 5px;
            }
        """ if self.current_theme == "dark" else """
            QMenu {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #d0d0d0;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ccc;
                margin-left: 5px;
                margin-right: 5px;
            }
        """

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        self.save_settings()

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 3
        self.move(x, y)

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.current_theme = settings.get("theme", "light")
                self.all_apps = settings.get("apps", [])
                self.window_width = settings.get("window_width", 700)
                self.window_title = settings.get("window_title", "Application Launcher")
        else:
            self.current_theme = "light"
            self.all_apps = []
            self.window_width = 700
            self.window_title = "Application Launcher"

    def save_settings(self):
        settings = {
            "theme": self.current_theme,
            "apps": self.all_apps,
            "window_width": self.width(),
            "window_title": self.window_title
        }
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)

    def add_application(self, app_info):
        self.all_apps.append(app_info)
        self.display_icons(self.all_apps)
        self.save_settings()

    def remove_application(self, app_info):
        self.all_apps = [app for app in self.all_apps if app != app_info]
        self.display_icons(self.all_apps)
        self.save_settings()

    def edit_application(self, app_info):
        dialog = AddEditIconDialog("Edit Application", self.current_theme, app_info, self)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if updated["name"] and updated["command"]:
                try:
                    index = self.all_apps.index(app_info)
                    self.all_apps[index] = updated
                    self.display_icons(self.all_apps)
                    self.save_settings()
                except ValueError:
                    QMessageBox.warning(self, "Error", "Application not found.")
            else:
                QMessageBox.warning(self, "Incomplete Input", "Please fill all fields.")

    def open_add_icon_dialog(self, prefill=None):
        dialog = AddEditIconDialog("Add Application", self.current_theme, prefill, self)
        if dialog.exec_() == QDialog.Accepted:
            app_info = dialog.get_data()
            if app_info["name"] and app_info["command"]:
                self.add_application(app_info)
            else:
                QMessageBox.warning(self, "Incomplete Input", "Please fill all fields.")

    def adjust_window_height(self):
        num_apps = len(self.all_apps)
        num_columns = 6
        num_rows = (num_apps + num_columns - 1) // num_columns
        icon_height = 100
        padding = 20
        header_height = 60
        new_height = padding + header_height + (num_rows * icon_height) + (
                    num_rows * 20) if num_apps else padding + header_height + 100
        new_height = max(200, min(new_height, 800))
        pos = self.pos()
        self.setFixedHeight(new_height)
        self.move(pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.x() >= self.width() - self._resize_margin and event.y() > 60:
                self._is_resizing = True
                self._resize_start_pos = event.globalPos()
                self._initial_width = self.width()
                event.accept()
            elif event.y() <= 60:
                self._is_dragging = True
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._is_resizing:
            delta = event.globalX() - self._resize_start_pos.x()
            new_width = self._initial_width + delta
            if self.minimumWidth() <= new_width <= self.maximumWidth():
                self.resize(new_width, self.height())
                self.adjust_window_height()
            event.accept()
        elif self._is_dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
        else:
            if event.x() >= self.width() - self._resize_margin and event.y() > 60:
                self.setCursor(QCursor(Qt.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event):
        if self._is_resizing:
            self._is_resizing = False
            self.save_settings()
            event.accept()
        if self._is_dragging:
            self._is_dragging = False
            event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.isfile(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    name = os.path.splitext(os.path.basename(file_path))[0]
                    app_info = {"name": name, "command": file_path, "icon": ""}
                    self.open_add_icon_dialog(prefill=app_info)
            event.acceptProposedAction()
        else:
            event.ignore()

    def title_mouse_press_event(self, event):
        if event.button() == Qt.RightButton:
            self.edit_title()

    def edit_title(self):
        self.title_edit = QLineEdit(self.window_title, self)
        font = self.title_edit.font()  # Ottiene il font corrente (predefinito del sistema)
        font.setPointSize(13)  # Imposta la dimensione del font
        self.title_edit.setFont(font)  #
        color = "#d3d3d3" if self.current_theme == "dark" else "#333333"
        self.title_edit.setStyleSheet(f"color: {color}; background-color: transparent;")
        self.title_edit.setFixedHeight(self.title_label.height())
        self.title_edit.returnPressed.connect(self.finish_edit_title)
        self.title_edit.focusOutEvent = self.finish_edit_title_focus_out
        self.title_label.hide()
        header_layout = self.centralWidget().layout().itemAt(0).layout()
        header_layout.insertWidget(0, self.title_edit)
        self.title_edit.setFocus()

    def finish_edit_title(self):
        new_title = self.title_edit.text().strip()
        if new_title:
            self.window_title = new_title
            self.title_label.setText(new_title)
        self.title_edit.deleteLater()
        self.title_label.show()
        self.save_settings()

    def finish_edit_title_focus_out(self, event):
        self.finish_edit_title()
        QLineEdit.focusOutEvent(self.title_edit, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppLauncher()
    window.show()
    sys.exit(app.exec_())
