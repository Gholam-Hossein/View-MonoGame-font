import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from font import MonoGameFont
from ui import FontRendererWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        fnt_file, _ = QFileDialog.getOpenFileName(
            None,
            "Select MonoGame Font File",
            os.path.expanduser("~"),
            "Font Files (*.json *.xnb);;All Files (*)"
        )
        if not fnt_file:
            sys.exit(0)
    else:
        fnt_file = sys.argv[1]

    if not os.path.isfile(fnt_file):
        QMessageBox.critical(None, "Error", f"فایل '{fnt_file}' وجود ندارد.")
        sys.exit(1)

    images_folder = os.path.dirname(fnt_file)
    try:
        font = MonoGameFont(fnt_file, images_folder)
        viewer = FontRendererWidget(font)
        viewer.show()
        app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"خطا در بارگذاری فونت: {e}")