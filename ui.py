from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QSlider, QScrollArea,
    QPushButton, QColorDialog, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from font_manager import FontManager
import recent_files

class FontRendererWidget(QWidget):
    def __init__(self, initial_font):
        super().__init__()
        self.font_manager = FontManager(initial_font)
        self.background_color = (50, 50, 50, 255)
        self.zoom_factor = 1.0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MonoGame Font Renderer")
        self.resize(800, 400)
        main_layout = QVBoxLayout()

        # منوی File
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Open", self.open_font)
        file_menu.addAction("Add Font", self.add_font)
        recent_menu = file_menu.addMenu("Open Recent")
        recent_files.populate_recent_menu(recent_menu, self.load_recent)
        file_menu.addAction("Remove All Fonts", self.font_manager.remove_all_fonts)
        main_layout.addWidget(menubar)

        # فیلدهای متنی
        self.text_fields_layout = QVBoxLayout()
        self.font_manager.add_text_field(self.text_fields_layout, self.update_render)
        self.font_manager.set_layout(self.text_fields_layout, self.update_render)

        # اسلایدر زوم و دکمه تغییر رنگ
        controls_layout = QVBoxLayout()
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom:")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        controls_layout.addLayout(zoom_layout)

        color_button = QPushButton("Change Color", self)
        color_button.clicked.connect(self.change_color)
        controls_layout.addWidget(color_button)

        # منطقه نمایش خروجی
        self.output_label = QLabel(self)
        self.output_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.output_label)
        scroll_area.setWidgetResizable(True)

        main_layout.addLayout(self.text_fields_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.update_render()

    def open_font(self):
        try:
            self.font_manager.open_font(self.text_fields_layout, self.update_render)
            self.update_render()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"خطا در باز کردن فونت: {e}")

    def add_font(self):
        try:
            self.font_manager.add_font(self.text_fields_layout, self.update_render)
            self.update_render()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"خطا در افزودن فونت: {e}")

    def load_recent(self, fnt_file):
        try:
            self.font_manager.load_recent_font(fnt_file, self.text_fields_layout, self.update_render)
            self.update_render()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"خطا در بارگذاری فونت اخیر: {e}")

    def on_zoom_changed(self):
        self.zoom_factor = self.zoom_slider.value() / 100.0
        self.update_render()

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = (color.red(), color.green(), color.blue(), 255)
            self.update_render()

    def update_render(self):
        pixmap = self.font_manager.render(self.background_color, self.zoom_factor)
        if pixmap:
            self.output_label.setPixmap(pixmap)
            self.output_label.resize(pixmap.width(), pixmap.height())
        else:
            self.output_label.clear()