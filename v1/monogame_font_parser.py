import json
import os
import subprocess
import sys
import shutil
from character import FontCharacter

def get_base_path():
    """یافتن مسیر پایه برای xnbcli.exe و temp با پشتیبانی از PyInstaller"""
    if getattr(sys, 'frozen', False):  # اگر به صورت .exe اجرا می‌شه
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_xnbcli_path():
    """یافتن مسیر xnbcli.exe"""
    base_path = get_base_path()
    xnbcli_path = os.path.join(base_path, 'App', 'xnbcli.exe')
    if not os.path.isfile(xnbcli_path):
        raise FileNotFoundError(f"xnbcli.exe در مسیر {xnbcli_path} پیدا نشد")
    return xnbcli_path

def extract_xnb_file(xnb_file, output_dir):
    """
    استخراج فایل .xnb به JSON با استفاده از xnbcli.exe
    
    Args:
        xnb_file (str): مسیر فایل .xnb
        output_dir (str): مسیر پوشه خروجی (temp)
    
    Returns:
        tuple: (مسیر فایل JSON, مسیر فایل PNG)
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        xnbcli_path = get_xnbcli_path()

        # بررسی وجود فایل PNG با نام مشابه .xnb
        xnb_basename = os.path.splitext(os.path.basename(xnb_file))[0]
        existing_png = os.path.join(os.path.dirname(xnb_file), f"{xnb_basename}.png")
        use_existing_png = os.path.isfile(existing_png)

        # ایجاد پوشه‌های موقت packed و unpacked
        packed_dir = os.path.join(output_dir, 'packed')
        unpacked_dir = os.path.join(output_dir, 'unpacked')
        os.makedirs(packed_dir, exist_ok=True)
        os.makedirs(unpacked_dir, exist_ok=True)

        # کپی فایل .xnb به پوشه packed
        xnb_filename = os.path.basename(xnb_file)
        packed_xnb = os.path.join(packed_dir, xnb_filename)
        with open(xnb_file, 'rb') as src, open(packed_xnb, 'wb') as dst:
            dst.write(src.read())

        # اجرای دستور unpack
        cmd = [xnbcli_path, 'unpack', packed_dir, unpacked_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"خروجی xnbcli: {result.stdout}")
            print(f"خطای xnbcli: {result.stderr}")
            raise RuntimeError(f"خطا در استخراج فایل .xnb: {result.stderr}")

        # یافتن فایل JSON تولیدشده
        json_file = None
        for root, _, files in os.walk(unpacked_dir):
            for file in files:
                if file.endswith('.json'):
                    json_file = os.path.join(root, file)
                    break
            if json_file:
                break

        if not json_file or not os.path.isfile(json_file):
            raise ValueError(f"فایل JSON در مسیر {unpacked_dir} پیدا نشد")

        # تعیین فایل PNG
        if use_existing_png:
            print(f"استفاده از فایل PNG موجود: {existing_png}")
            png_file = existing_png
        else:
            # یافتن فایل PNG تولیدشده
            png_file = None
            for root, _, files in os.walk(unpacked_dir):
                for file in files:
                    if file.endswith('.png'):
                        png_file = os.path.join(root, file)
                        break
                if png_file:
                    break
            if not png_file or not os.path.isfile(png_file):
                raise ValueError(f"فایل PNG در مسیر {unpacked_dir} پیدا نشد")
            
            # کپی PNG به دایرکتوری فایل اصلی
            dest_png = os.path.join(os.path.dirname(xnb_file), os.path.basename(png_file))
            with open(png_file, 'rb') as src, open(dest_png, 'wb') as dst:
                dst.write(src.read())
            print(f"کپی فایل PNG به: {dest_png}")
            png_file = dest_png

        return json_file, png_file

    except Exception as e:
        raise ValueError(f"خطا در استخراج فایل .xnb {xnb_file}: {e}")

def parse_monogame_fnt(filename, chars, pages):
    """
    پردازش فایل فونت JSON یا .xnb تولیدشده توسط MonoGame.
    
    Args:
        filename (str): مسیر فایل JSON یا .xnb
        chars (dict): دیکشنری برای ذخیره اشیاء FontCharacter
        pages (dict): دیکشنری برای ذخیره نام فایل‌های تصویر
    """
    temp_dir = os.path.join(get_base_path(), 'App', 'temp')
    json_file = filename
    temp_png = None

    try:
        if filename.endswith('.xnb'):
            json_file, temp_png = extract_xnb_file(filename, temp_dir)
            if temp_png:
                pages[0] = os.path.basename(temp_png)

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                font_data = json.load(f)
        except Exception as e:
            raise ValueError(f"خطا در پردازش فایل JSON {json_file}: {e}")

        content = font_data.get("content", {})

        if not content.get("glyphs") or not content.get("characterMap"):
            raise ValueError("فایل JSON فاقد داده‌های گلیف یا نگاشت کاراکتر است")

        if not filename.endswith('.xnb'):
            texture_info = content.get("texture", {})
            texture_file = texture_info.get("export")
            if not texture_file:
                raise ValueError("فایل JSON فاقد نام فایل تصویر است")
            pages[0] = texture_file

        glyphs_data = content.get("glyphs", [])
        cropping_data = content.get("cropping", [])
        character_map = content.get("characterMap", [])
        horizontal_spacing = content.get("horizontalSpacing", 0)

        for i, char in enumerate(character_map):
            if i >= len(glyphs_data):
                continue
            glyph = glyphs_data[i]
            crop = cropping_data[i] if i < len(cropping_data) else {}

            c = FontCharacter(
                id=ord(char),
                x=glyph.get('x', 0),
                y=glyph.get('y', 0),
                width=glyph.get('width', 0),
                height=glyph.get('height', 0),
                xoffset=crop.get('x', 0),
                yoffset=crop.get('y', 0),
                xadvance=int(glyph.get('width', 0) + horizontal_spacing),
                page=0
            )
            chars[c.id] = c

    finally:
        # پاک‌سازی پوشه temp فقط برای .xnb
        if filename.endswith('.xnb'):
            shutil.rmtree(temp_dir, ignore_errors=True)