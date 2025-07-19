import os
from PIL import Image
from monogame_font_parser import parse_monogame_fnt

class MonoGameFont:
    def __init__(self, fnt_file, images_folder):
        self.chars = {}
        self.pages = {}
        self.images_folder = images_folder
        self.parse_fnt(fnt_file)
        self.load_pages()

    def parse_fnt(self, filename):
        if not (filename.endswith('.json') or filename.endswith('.xnb')):
            raise ValueError("فقط فایل‌های JSON و .xnb پشتیبانی می‌شوند")
        parse_monogame_fnt(filename, self.chars, self.pages)

    def load_pages(self):
        if not self.pages:
            raise ValueError("هیچ فایل تصویری برای فونت پیدا نشد. لطفاً مطمئن شوید فایل PNG کنار فایل .xnb یا .json وجود دارد.")
        for pid, fname in list(self.pages.items()):
            path = os.path.join(self.images_folder, fname)
            if os.path.isfile(path):
                try:
                    im = Image.open(path).convert("RGBA")
                    self.pages[pid] = im
                    print(f"بارگذاری فایل PNG: {path}")
                except Exception as e:
                    print(f"خطا در بارگذاری {path}: {e}")
                    self.pages[pid] = None
            else:
                print(f"فایل تصویر وجود ندارد: {path}")
                self.pages[pid] = None

    def render_text(self, text, background_color=(50, 50, 50, 255)):
        width = 0
        max_top = 0
        max_bottom = 0
        chars_for_render = []

        for ch in text:
            cid = ord(ch)
            c = self.chars.get(cid)
            if not c:
                space = self.chars.get(ord(" "))
                if space:
                    width += space.xadvance
                continue
            if self.pages.get(c.page) is None:
                width += c.xadvance
                continue
            chars_for_render.append(c)
            width += c.xadvance
            top = -c.yoffset
            bottom = c.height + c.yoffset
            if top > max_top:
                max_top = top
            if bottom > max_bottom:
                max_bottom = bottom

        height = max_top + max_bottom
        if height == 0 or not chars_for_render:
            return Image.new("RGBA", (100, 20), background_color)

        out_img = Image.new("RGBA", (width, height), background_color)

        x_cursor = 0
        for c in chars_for_render:
            img_page = self.pages.get(c.page)
            char_img = img_page.crop((c.x, c.y, c.x + c.width, c.y + c.height))
            y_pos = max_top + c.yoffset
            out_img.paste(char_img, (x_cursor + c.xoffset, y_pos), char_img)
            x_cursor += c.xadvance

        return out_img