import os
from PyQt5.QtWidgets import QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
from font import MonoGameFont
from renderer import render_fonts
import recent_files

class FontManager:
    def __init__(self, initial_font):
        self.fonts = [initial_font]
        self.text_fields = []
        self.field_layouts = []
        self.text_fields_layout = None
        self.update_callback = None
        self.last_folder = os.path.expanduser("~")

    def add_text_field(self, parent_layout, update_callback):
        field_layout = QHBoxLayout()
        text_field = QLineEdit("Hello")
        text_field.textChanged.connect(update_callback)
        field_layout.addWidget(text_field)
        if len(self.text_fields) > 0:
            remove_button = QPushButton("X")
            remove_button.setFixedWidth(20)
            remove_button.clicked.connect(lambda: self.remove_font_by_field(text_field))
            field_layout.addWidget(remove_button)
        parent_layout.addLayout(field_layout)
        self.text_fields.append(text_field)
        self.field_layouts.append(field_layout)

    def load_font(self, parent_layout, update_callback, mode="add", fnt_file=None):
        if not fnt_file:
            fnt_file, _ = QFileDialog.getOpenFileName(
                None, "Select MonoGame Font File", self.last_folder, "Font Files (*.json *.xnb);;All Files (*)"
            )
        if not fnt_file:
            return
        try:
            font = MonoGameFont(fnt_file, os.path.dirname(fnt_file))
            if mode == "add":
                self.fonts.append(font)
            else:
                self.fonts = [font]
                self.clear_fields(parent_layout)
                self.text_fields = []
                self.field_layouts = []
            self.add_text_field(parent_layout, update_callback)
            recent_files.save_recent_file(fnt_file)
            self.last_folder = os.path.dirname(fnt_file)
            self.set_layout(parent_layout, update_callback)
            self.update_callback()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"خطا در بارگذاری فونت: {e}. لطفاً مطمئن شوید فایل .xnb یا .json و فایل PNG مرتبط (مثل {os.path.splitext(os.path.basename(fnt_file))[0]}.png) معتبر هستند.")

    def add_font(self, parent_layout, update_callback):
        self.load_font(parent_layout, update_callback, mode="add")

    def open_font(self, parent_layout, update_callback):
        self.load_font(parent_layout, update_callback, mode="open")

    def load_recent_font(self, fnt_file, parent_layout, update_callback):
        self.load_font(parent_layout, update_callback, mode="recent", fnt_file=fnt_file)

    def remove_font_by_field(self, text_field):
        try:
            index = self.text_fields.index(text_field)
            if len(self.fonts) <= 1 or index == 0:
                return
            self.fonts.pop(index)
            self.text_fields.pop(index)
            field_layout = self.field_layouts.pop(index)
            self.text_fields_layout.removeItem(field_layout)
            for i in range(field_layout.count()):
                if widget := field_layout.itemAt(i).widget():
                    widget.deleteLater()
            field_layout.deleteLater()
            self.update_callback()
        except ValueError:
            QMessageBox.critical(None, "Error", "خطا در حذف فونت")

    def remove_all_fonts(self):
        if len(self.fonts) <= 1:
            return
        self.fonts = [self.fonts[0]]
        self.clear_fields(self.text_fields_layout)
        self.text_fields = []
        self.field_layouts = []
        self.add_text_field(self.text_fields_layout, self.update_callback)
        self.update_callback()

    def clear_fields(self, parent_layout):
        for field_layout in self.field_layouts:
            parent_layout.removeItem(field_layout)
            while field_layout.count():
                if widget := field_layout.itemAt(0).widget():
                    widget.deleteLater()
                field_layout.removeItem(field_layout.itemAt(0))
            field_layout.deleteLater()

    def set_layout(self, layout, callback):
        self.text_fields_layout = layout
        self.update_callback = callback

    def render(self, background_color, zoom_factor):
        pixmap = render_fonts(self.fonts, self.text_fields, background_color, zoom_factor)
        if pixmap.isNull():
            QMessageBox.warning(None, "Warning", "هیچ کاراکتری برای رندر یافت نشد یا فایل تصویر فونت موجود نیست. لطفاً کاراکترهای پشتیبانی‌شده را وارد کنید.")
        return pixmap