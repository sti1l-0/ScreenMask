import tkinter as tk
from screeninfo import Monitor
import logging


class MaskWindow:
    def __init__(self, root: tk.Tk, monitor: Monitor):
        self.window = None
        self.create_window(root, monitor)

    def create_window(self, root: tk.Tk, monitor: Monitor):
        """创建遮罩窗口"""
        try:
            self.window = tk.Toplevel(root)
            self.window.withdraw()
            self.setup_window(monitor)
        except Exception as e:
            logging.error(f"创建遮罩窗口失败: {str(e)}")
            raise

    def setup_window(self, monitor: Monitor):
        """设置遮罩窗口的属性"""
        try:
            self.window.attributes("-alpha", 0.9)
            self.window.attributes("-topmost", True)
            self.window.overrideredirect(True)
            self.window.configure(bg="black")

            geometry = f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
            self.window.geometry(geometry)
        except Exception as e:
            logging.error(f"设置遮罩窗口属性失败: {str(e)}")
            raise

    def show(self):
        """显示遮罩窗口"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.deiconify()
        except Exception as e:
            logging.error(f"显示遮罩窗口失败: {str(e)}")

    def hide(self):
        """隐藏遮罩窗口"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.withdraw()
        except Exception as e:
            logging.error(f"隐藏遮罩窗口失败: {str(e)}")

    def destroy(self):
        """销毁遮罩窗口"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.destroy()
                self.window = None
        except Exception as e:
            logging.error(f"销毁遮罩窗口失败: {str(e)}")
            # 确保窗口引用被清除
            self.window = None

    def set_opacity(self, value: float):
        """设置窗口透明度"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.attributes("-alpha", value)
        except Exception as e:
            logging.error(f"设置透明度失败: {str(e)}")
