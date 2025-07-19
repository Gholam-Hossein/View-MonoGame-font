import os
import subprocess
import shutil
import uuid
from pathlib import Path

class XNBHandler:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.data_dir = os.path.join(project_dir, "Data")
        self.xnbcli_path = os.path.join(project_dir, "App", "xnbcli.exe")
        self.extract_temp = None
        self.pack_temp = None
        self.create_temp_folders()

    def create_temp_folders(self):
        """ساخت پوشه‌های موقت با نام‌های رندوم"""
        os.makedirs(self.data_dir, exist_ok=True)
        self.extract_temp = os.path.join(self.data_dir, f"extract_temp_{uuid.uuid4().hex}")
        self.pack_temp = os.path.join(self.data_dir, f"pack_temp_{uuid.uuid4().hex}")
        os.makedirs(self.extract_temp)
        os.makedirs(self.pack_temp)

    def cleanup(self):
        """حذف پوشه‌های موقت"""
        for temp_dir in [self.extract_temp, self.pack_temp]:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def extract_xnb(self, xnb_file):
        """استخراج فایل .xnb به پوشه موقت استخراج"""
        if not os.path.isfile(xnb_file):
            raise ValueError(f"فایل {xnb_file} وجود ندارد")
        if not os.path.isfile(self.xnbcli_path):
            raise ValueError(f"xnbcli.exe در مسیر {self.xnbcli_path} پیدا نشد")

        # کپی فایل .xnb به پوشه استخراج
        dest_xnb = os.path.join(self.extract_temp, os.path.basename(xnb_file))
        shutil.copy(xnb_file, dest_xnb)

        # اجرای xnbcli برای استخراج
        try:
            subprocess.run(
                [self.xnbcli_path, "unpack", dest_xnb, self.extract_temp],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(f"خطا در استخراج فایل .xnb: {e.stderr}")

        # برگرداندن مسیر فایل JSON استخراج‌شده
        json_files = [f for f in os.listdir(self.extract_temp) if f.endswith('.json')]
        if not json_files:
            raise ValueError("هیچ فایل JSON در خروجی استخراج یافت نشد")
        return os.path.join(self.extract_temp, json_files[0])

    def pack_xnb(self, json_file, output_xnb_path):
        """ذخیره فایل JSON و PNG به .xnb"""
        if not os.path.isfile(json_file):
            raise ValueError(f"فایل JSON {json_file} وجود ندارد")
        if not os.path.isdir(self.pack_temp):
            raise ValueError("پوشه ذخیره موقت وجود ندارد")

        # کپی فایل‌های JSON و PNG به پوشه pack
        shutil.rmtree(self.pack_temp, ignore_errors=True)
        os.makedirs(self.pack_temp)
        shutil.copy(json_file, self.pack_temp)
        json_base = os.path.splitext(os.path.basename(json_file))[0]
        png_file = os.path.join(os.path.dirname(json_file), f"{json_base}.png")
        if os.path.isfile(png_file):
            shutil.copy(png_file, self.pack_temp)

        # اجرای xnbcli برای ذخیره
        try:
            subprocess.run(
                [self.xnbcli_path, "pack", json_file, self.pack_temp],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(f"خطا در ذخیره فایل .xnb: {e.stderr}")

        # انتقال فایل .xnb تولیدشده به مسیر خروجی
        xnb_files = [f for f in os.listdir(self.pack_temp) if f.endswith('.xnb')]
        if not xnb_files:
            raise ValueError("هیچ فایل XNB تولید نشد")
        shutil.move(os.path.join(self.pack_temp, xnb_files[0]), output_xnb_path)