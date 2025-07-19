from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

def render_fonts(fonts, text_fields, background_color, zoom_factor):
    total_height = 0
    max_width = 0
    images = []

    for font, text_field in zip(fonts, text_fields):
        text = text_field.text()
        img = font.render_text(text, background_color=background_color)
        if img:
            images.append(img)
            total_height += img.height
            max_width = max(max_width, img.width)

    if not images:
        return QPixmap.fromImage(QImage(100, 20, QImage.Format_RGBA8888))

    combined_img = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))
    y_offset = 0
    for img in images:
        combined_img.paste(img, (0, y_offset))
        y_offset += img.height

    data = combined_img.tobytes("raw", "RGBA")
    qimg = QImage(data, combined_img.width, combined_img.height, QImage.Format_RGBA8888)
    pixmap = QPixmap.fromImage(qimg)
    if pixmap.isNull():
        return QPixmap.fromImage(QImage(100, 20, QImage.Format_RGBA8888))

    scaled_pixmap = pixmap.scaled(
        int(pixmap.width() * zoom_factor),
        int(pixmap.height() * zoom_factor),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    return scaled_pixmap